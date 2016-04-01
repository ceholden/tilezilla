""" Database query operations
"""
import click

from . import options


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
    db = _db_from_ctx(ctx)

    click.echo('Information about: {}'.format(table))
    query = db.session.query(table).filter_by(**filter_)

    click.echo('Number of entries: {}'.format(query.count()))


@db.command(short_help='Search database')
@options.arg_db_table
@options.opt_db_filter
@click.pass_context
def search(ctx, filter_, table):
    """ Search a table according to some filters

    Example: search the "product" table for a given product ID
    """
    db = _db_from_ctx(ctx)

    click.echo('Search: "{}" where:\n{}'.format(table, filter_))
    query = db.session.query(table).filter_by(**filter_)
    for query_row in query:
        from IPython.core.debugger import Pdb; Pdb().set_trace()
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
