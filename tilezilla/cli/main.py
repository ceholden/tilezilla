import logging
from pkg_resources import iter_entry_points

import click
import click_plugins

from . import options
from .. import __version__

_context = dict(
    token_normalize_func=lambda x: x.lower(),
    help_option_names=['--help', '-h']
)


@click_plugins.with_plugins(ep for ep in
                            iter_entry_points('tilez.commands'))
@click.group(help='tilezilla command line interface',
             context_settings=_context)
@options.opt_config_file
@click.option('--verbose', '-v', is_flag=True, help='Be verbose')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.version_option(__version__)
@click.pass_context
def cli(ctx, verbose, quiet):
    # Logging config
    logging.basicConfig()
    logger = logging.getLogger('tilezilla')
    if verbose:
        logger.setLevel(logging.DEBUG)
    if quiet:
        logger.setLevel(logging.WARNING)
