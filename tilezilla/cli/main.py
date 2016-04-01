import logging
from pkg_resources import iter_entry_points

import click
import click_plugins

from . import options
from .. import __version__

_context = dict(
    token_normalize_func=lambda x: x.lower(),
    help_option_names=['--help', '-h'],
    auto_envvar_prefix='TILEZILLA'
)

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'


@click_plugins.with_plugins(ep for ep in
                            iter_entry_points('tilez.commands'))
@click.group(help='tilezilla command line interface',
             context_settings=_context)
@options.opt_config_file
@click.option('--verbose', '-v', count=True, help='Be louder')
@click.option('--quiet', '-q', count=True, help='Be quieter')
@click.version_option(__version__)
@click.pass_context
def cli(ctx, config_file, verbose, quiet):
    verbosity = verbose - quiet
    log_level = 20 - 10 * verbosity

    # Logging config for tilez
    logger = logging.getLogger('tilez')
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    handler = logging.StreamHandler(click.get_text_stream('stdout'))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(max(10, log_level))  # never below DEBUG (10)

    # Logging for main module
    main_logger = logging.getLogger('tilezilla')
    if log_level <= 0:  # log_level=NOSET (0) sets main logger to debug
        main_logger.setLevel(logging.DEBUG)

    # Parse config
    ctx.obj = ctx.obj or {}
    if config_file:
        from ..config import parse_config
        ctx.obj['config'] = parse_config(config_file)
