import logging
from pkg_resources import iter_entry_points

import click
import click_plugins

import landsat_tile

_context = dict(
    token_normalize_func=lambda x: x.lower(),
    help_option_names=['--help', '-h']
)


@click_plugins.with_plugins(ep for ep in
                            iter_entry_points('landsat_tile.commands'))
@click.group(help='Landsat tile preprocessing command line interface (CLI)',
             context_settings=_context)
@click.version_option(landsat_tile.__version__)
@click.option('--verbose', '-v', is_flag=True, help='Be verbose')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.pass_context
def cli(ctx, verbose, quiet):
    # Logging config
    logging.basicConfig()
    logger = logging.getLogger('landsat_tile')
    if verbose:
        logger.setLevel(logging.DEBUG)
    if quiet:
        logger.setLevel(logging.WARNING)
