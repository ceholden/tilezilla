""" Database query operations
"""
import logging

import click
import six
import sqlalchemy as sa

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

    from IPython.core.debugger import Pdb; Pdb().set_trace()


@db.command(short_help='Search database')
@options.arg_db_table
@options.opt_db_filter
@click.pass_context
def search(ctx, filter_, table):
    """ Search a table according to some filters

    Example: search the "product" table for a given product ID
    """
    from ..db import convert_query_type

    db = _db_from_ctx(ctx)

    click.echo('Search: "{}" where:\n{}'.format(table, filter_))

    # Convert/cast filter query values as needed
    from IPython.core.debugger import Pdb; Pdb().set_trace()
    for k in filter_:
        filter_[k] = convert_query_type(table, k, filter_[k])

    query = db.session.query(table).filter(**filter_)
    for query_row in query:
        print(query_row)


@db.command(short_help='Search database and return IDs')
@options.arg_db_table
@options.opt_db_filter
@click.pass_context
def id(ctx, filter_, table):
    """ Useful for piping into `tilez spew`
    """
    db = _db_from_ctx(ctx)
    ctx.forward(search)
