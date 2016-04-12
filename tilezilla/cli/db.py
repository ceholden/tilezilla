""" Database query operations
"""
import logging

import click
import six

from . import cliutils, options


def _db_from_ctx(ctx):
    try:
        db = ctx.obj['db']
    except Exception as e:
        raise click.BadParameter('Must specify config file: {}'.format(e),
                                 param=options.opt_config_file)
    return db


@click.group(help='Database information and queries')
@click.pass_context
def db(ctx):
    if ctx.obj and ctx.obj.get('config', {}):
        # Init database and stick in context for sub-commands
        from ..db import Database
        ctx.obj['db'] = Database.from_config(ctx.obj['config']['database'])


@db.command(short_help='Print database information')
@options.opt_db_filter
@options.arg_db_table
@click.pass_context
def info(ctx, table, filter_):
    """ Print table summary information
    """
    import sqlalchemy_utils as sau
    db = _db_from_ctx(ctx)
    echoer = cliutils.Echoer(logging.getLogger('tilez'))

    echoer.info('Information about: {}'.format(table))
    query = db.session.query(table).filter_by(**filter_)

    echoer.process('Number of entries: {}'.format(query.count()))

    # Diagnostic info about table
    template = '{idx: <10} {name: <20}{type: <15}'

    echoer.process('Enumerating columns in table: {}'.format(table))
    echoer.item('{idx: <10} {name: <20}{type: <30}'
                .format(idx='COLUMN #', name='NAME', type='TYPE'),
                bold=True, underline=True)
    for idx, col in enumerate(sau.get_columns(table).values()):
        echoer.item(template.format(**{
            'idx': 'Col {0:02d}'.format(idx),
            'name': '"{}"'.format(col.name),
            'type': '{type} {pk}'.format(
                type=col.type, pk='(PRIMARY KEY)' if col.primary_key else '')
        }))

    for idx, (name, col) in enumerate(six.iteritems(
            sau.get_hybrid_properties(table))):
        echoer.item(template.format(**{
            'idx': 'HYBRID {0:02d}'.format(idx),
            'name': '"{}"'.format(name),
            'type': '?'
        }))


@db.command(short_help='Search database')
@options.arg_db_table
@options.opt_db_select
@options.opt_db_filter
@options.opt_db_distinct
@options.opt_db_groupby
@click.option('--quiet', '-q', is_flag=True, help='Suppress excessive text')
@click.pass_context
def search(ctx, quiet, group_by, distinct, filter_, select, table):
    """ Search a table according to some filters

    Example:

    \b
    1. Print list of all products with 8 bands, grouped by 'timeseries_id'
        > tilez db search -h --filter "n_bands = 8"
            --group_by timeseries_id product

    """
    # TODO: add conjunction argument -- or / and
    import sqlalchemy_utils as sau
    from ..db import construct_filter

    db = _db_from_ctx(ctx)
    table_columns = sau.get_columns(table)

    if '*' in select:
        select = table_columns.keys()

    if not quiet:
        click.secho('Searching table "{}" where:'.format(table.__tablename__),
                    fg='blue', bold=True)
        for filter_item in filter_:
            click.echo('    {}'.format(filter_item))

    query = construct_filter(db.session.query(table), filter_)

    if distinct:
        try:
            col = table_columns[distinct]
        except KeyError:
            raise click.BadParameter(
                'Cannot select distinct of "{}" in table "{}": no such column'
                .format(distinct, table), param_hint='distinct')
        else:
            query = query.distinct(col)

    if group_by:
        try:
            col = table_columns[group_by]
        except KeyError:
            raise click.BadParameter(
                'Cannot group by "{}" in table "{}": no such column'
                .format(group_by, table), param_hint='group_by')
        else:
            query = query.group_by(col)

    if not quiet:
        click.secho('Results:', fg='red', bold=True)
    for query_row in query:
        if select and not quiet:
            click.echo(', '.join('{}={}'.format(_c, getattr(query_row, _c))
                       for _c in select))
        elif select and quiet:
            click.echo(' '.join(str(getattr(query_row, _c)) for _c in select))
        else:
            click.echo(query_row)


@db.command(short_help='Search database and return IDs')
@options.arg_db_table
@options.opt_db_filter
@options.opt_db_distinct
@options.opt_db_groupby
@click.pass_context
def id(ctx, group_by, distinct, filter_, table):
    """ Useful for piping into `tilez spew`
    """
    ctx.forward(search, select=('id', ), quiet=True)
