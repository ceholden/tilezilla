""" Database query operations
"""
import click

from . import options
from ..db import TABLES, Database


@click.group(help='Database information and queries')
@options.pass_config
@click.pass_context
def db(ctx, config):
    # Stick in context for sub-commands
    ctx.obj['db'] = Database.from_config(config['database'])


@db.command(short_help='Print database information')
@options.arg_db_table
@options.pass_db
@options.pass_config
def info(config, db, table):
    """ Print table information, like the table fields
    """
    print('Info: "{}"'.format(table))


@db.command(short_help='Search database')
@options.arg_db_table
@options.opt_db_filter
@options.pass_db
@options.pass_config
def search(config, db, filter_, table):
    """ Search a table according to some filters

    Example: search the "product" table for a given product ID
    """
    print('Search: "{}" where:\n{}'.format(table, filter_))
    query = db.session.query(TABLES[table]).filter_by(**filter_)
    for query_row in query:
        from IPython.core.debugger import Pdb; Pdb().set_trace()
        print(query_row)


@db.command(short_help='Search database and return IDs')
@options.arg_db_table
@options.opt_db_filter
@options.pass_db
@options.pass_config
@click.pass_context
def id(ctx, config, db, filter_, table):
    """ Useful for piping into `tilez spew`
    """
    ctx.forward(search)
