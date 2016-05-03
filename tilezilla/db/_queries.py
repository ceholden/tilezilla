""" Helpers for guessing our way into queries against the database
"""
import ast
import logging
import re

import arrow
import six
import sqlalchemy as sa
import sqlalchemy_utils as sau

from ._tables import TABLES

logger = logging.getLogger('tilezilla')

DATETIME_TYPES = (sa.sql.sqltypes.DateTime,
                  sa.sql.sqltypes.Date,
                  sau.ArrowType)

COMPARATORS = ['eq', 'ne', 'le', 'lt', 'ge', 'gt', 'in', 'like']


# Database linkages as graph ---------------------------------------------------
def _make_table_graph(tables):
    graph = {}
    for t in tables:
        relations = sa.inspect(t).relationships
        graph[t] = [relation.mapper.class_ for relation in relations]
    return graph


def _link_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = _link_path(graph, node, end, path)
            if newpath: return newpath
    return None

TABLES_GRAPH = _make_table_graph(TABLES.values())


# [KEY]
# 1. PARSE SYSTEM --------------------------------------------------------------
def _convert_expression_operator(expr):
    """ Convert expression operators from '=' style to 'eq' style
    Args:
        expr (str): Expression to convert
    Returns:
        str: Converted expression
    """
    TO_CONVERT = {
        ' eq ': ['=', '=='],
        ' ne ': ['!=', '=!'],
        ' lt ': ['<'],
        ' le ': ['<=', '=<'],
        ' gt ': ['>'],
        ' ge ': ['>=', '=>']
    }
    for op, matches in six.iteritems(TO_CONVERT):
        for match in matches:
            if match in expr:
                return expr.replace(match, op)
    return expr


def _parse_expression_filter(expr):
    """ Convert a filter expression into [KEY], [OPERATOR], [VALUE...]

    Args:
        str: A filter expression

    Returns:
        tuple (str, str, str): The key, operator, and value or values

    Raises:
        KeyError: Raise if operator not in available comparators
            (:attr:`COMPARATORS`)
    """
    # Parse operator
    for comp in COMPARATORS:
        split = re.split('\s(?i)%s\s' % comp, expr)
        if len(split) == 2:
            return split[0].strip(), comp, split[1].lstrip()
    raise KeyError('Could not find a supported comparator in expression')


def _tablename_to_class(base, tablename):
    """ Return class of tablename
    """
    for c in base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


# [VALUE]
# TYPE CAST SYSTEM
def convert_query_type(column, value):
    """ Return `value` converted to type expected by `table` for column `key`

    Args:
        column (sqlalchemy.orm.attributes.QueryableAttribute): A SQLAlchemy
            ORM attribute
        value (str): A value to convert

    Returns:
        type: `value`, converted to a different type
    """
    if isinstance(column.type, DATETIME_TYPES):
        return arrow.get(value).datetime
    elif isinstance(column.type, sau.ScalarListType):
        try:
            value = ast.literal_eval(value)
        except SyntaxError as exc:
            logger.error(exc)
            raise SyntaxError('Cannot convert column {} - invalid syntax: {}'
                              .format(column, value))
        else:
            return value
    return sau.cast_if(value, type(column.type))


# [FUNCTION]
# The thing to write that uses above
def construct_filter(query, items, conjunction='and'):
    """ Construct a filter from a combination of filter items

    Args:
        query (sqlalchemy.orm.query.Query): The SQLAlchemy SQL ORM object
        items (list[str]): List of query expressions in form of
            "[KEY][OPERATOR][VALUE...]"
        conjunction (str): Combine the filter items using 'and' or 'or'

    Returns:
        sqlalchemy.orm.query.Query: A query with filter items applied

    Raises:
        KeyError: Raise if column given in filter expression does not exist
    """
    # Find table model
    entities = sau.get_query_entities(query)
    if len(entities) > 1:
        logger.warning('Using first entity from search query ({})'
                       .format(entities[0]))
    table = entities[0]
    base = sau.get_declarative_base(table)

    # Parse expressions
    items = [_convert_expression_operator(item) for item in items]
    exprs = [_parse_expression_filter(item) for item in items]

    filters = []
    joins = set([])
    for key, operator, value in exprs:
        # Preprocess case of linked table
        if '.' in key:
            _tablename, key = key.split('.', maxsplit=1)
            _table = _tablename_to_class(base, _tablename)
            joins.update([t for t in _link_path(TABLES_GRAPH, table, _table)
                          if t is not table])
        else:
            _table = table

        column = getattr(_table, key, None)
        if column is None:
            raise KeyError('Cannot construct filter: column "{}" does not '
                           'exist'.format(key))

        if operator.lower() == 'in':
            value = [convert_query_type(column, v) for v in
                     value.replace(' ', ',').split(',') if v]
            filter_item = column.in_(value)
        else:
            attr = [pattern % operator for pattern in
                    ('%s', '%s_', '__%s__')
                    if hasattr(column, pattern % operator)]
            if not attr:
                raise KeyError('Cannot construct filter: column {} is not '
                               'usable with "{}"'.format(key, operator))
            if value.lower() in ('null', 'none', 'na', 'nan'):
                value = None
            else:
                value = convert_query_type(column, value)
            filter_item = getattr(column, attr[0])(value)
        filters.append(filter_item)

    for join_table in joins:
        query = query.join(join_table)
    if conjunction == 'or':
        return query.filter(sa.or_(*filters))
    else:
        return query.filter(sa.and_(*filters))
