""" Helpers for guessing our way into queries against the database
"""
import logging
import re

import arrow
import six
import sqlalchemy as sa
import sqlalchemy_utils as sau

logger = logging.getLogger('tilezilla')

# [OP]
# 1. REGEX
COMPARATORS = ['eq', 'ne', 'le', 'lt', 'ge', 'gt', 'in', 'like']


# [KEY]
# 1. PARSE SYSTEM
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
            return split[0].strip(), comp, split[1]
    raise KeyError('Could not find a supported comparator in expression')


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
    if isinstance(column.type, (sa.sql.sqltypes.DateTime,
                                sa.sql.sqltypes.Date)):
        return arrow.get(value).datetime
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
    # Parse expressions
    items = [_convert_expression_operator(item) for item in items]
    exprs = [_parse_expression_filter(item) for item in items]

    # Find table model
    entities = sau.get_query_entities(query)
    if len(entities) > 1:
        logger.warning('Using first entity from search query ({})'
                       .format(entities[0]))
    table = entities[0]

    filters = []
    for key, operator, value in exprs:
        column = getattr(table, key, None)
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

    if conjunction == 'or':
        return query.filter(sa.or_(*filters))
    else:
        return query.filter(sa.and_(*filters))
