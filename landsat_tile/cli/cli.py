""" Command line interface commands
"""
import logging

import click

logger = logging.getLogger('landsat_tile')


@click.command(short_help='Unzip and organize a Landsat dataset')
@click.argument('archive', type=click.Path(dir_okay=False, resolve_path=True,
                                           readable=True))
@click.pass_context
def unzip(ctx, archive):
    """ Unzip and organize an archive by Landsat ID
    """
    pass


@click.command(short_help='Batch tile a Landsat archive')
@click.pass_context
def batch(ctx):
    """ Batch tile a Landsat archive according to JSON parameter file
    """
    pass
