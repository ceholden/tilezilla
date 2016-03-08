""" Database query operations
"""
import click

from .options import callback_dict
from ..db import TABLES

opt_db_table = click.argument('table', type=click.Choice(TABLES.keys()))


@click.group(help='test')
@click.pass_context
def db(ctx):
    pass


@db.command(short_help='Print database information')
@opt_db_table
@click.pass_context
def info(ctx, table):
    print('Info: "{}"'.format(table))


@db.command(short_help='Search database')
@opt_db_table
@click.option('--filter', 'filter_', type=str,
              callback=callback_dict, multiple=True,
              help='Fitler TABLE by attr=value')
@click.pass_context
def search(ctx, filter_, table):
    print('Search: "{}" where:\n{}'.format(table, filter_))
