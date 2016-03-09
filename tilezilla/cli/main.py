import logging
from pkg_resources import iter_entry_points

import click
import click_plugins

from .. import __version__
from ..config import parse_config

_context = dict(
    token_normalize_func=lambda x: x.lower(),
    help_option_names=['--help', '-h']
)


@click_plugins.with_plugins(ep for ep in
                            iter_entry_points('tilez.commands'))
@click.group(help='tilezilla command line interface',
             context_settings=_context)
@click.option('--config', 'config_file',
              envvar='TILEZILLA_CONFIG', show_default=True,
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              help='Configuration file (or, as TILEZILLA_CONFIG envvar)')
@click.option('--verbose', '-v', is_flag=True, help='Be verbose')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.version_option(__version__)
@click.pass_context
def cli(ctx, config_file, verbose, quiet):
    if not config_file:
        raise click.BadParameter('Must specify a configuration file',
                                 param_hint='config_file')
    # Pass configuration file
    config = parse_config(config_file)
    ctx.obj = dict(config=config, config_file=config_file)

    # Logging config
    logging.basicConfig()
    logger = logging.getLogger('tilezilla')
    if verbose:
        logger.setLevel(logging.DEBUG)
    if quiet:
        logger.setLevel(logging.WARNING)
