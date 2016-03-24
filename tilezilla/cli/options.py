import functools

import click

from .. import multiprocess


# PASS
def pass_config(f):
    """ Parse tilezilla config from config_file opt and pass as first arg
    """
    from ..config import parse_config
    @functools.wraps(f)
    def _parse_config(*args, **kwargs):
        config_file = click.get_current_context().obj['config_file']
        if not config_file:
            raise click.BadParameter('Must specify a configuration file',
                                     param_hint='config')
        try:
            config = parse_config(config_file)
        except Exception:
            msg = click.style('Could not parse the config file ({}).'
                              '\nTraceback'.format(config_file),
                              fg='red')
            click.echo(msg)
            raise
        return f(config, *args, **kwargs)

    return _parse_config

def pass_db(f):
    """ Grab database instance from ctx and return as first arg
    """
    @functools.wraps(f)
    def _get_db(*args, **kwargs):
        db = click.get_current_context().obj['db']
        return f(db, *args, **kwargs)

    return _get_db

# CALLBACKS
def callback_dict(ctx, param, value):
    """ Call back for dict style arguments (e.g., KEY=VALUE)
    """
    if not value:
        return {}
    else:
        d = {}
        for val in value:
            if '=' not in val:
                raise click.BadParameter(
                    'Must specify {p} as KEY=VALUE ({v} given)'.format(
                        p=param, v=value))
            else:
                k, v = val.split('=', 1)
                d[k] = v
        return d


def callback_db_table(ctx, param, value):
    """ Return database table class
    """
    from ..db import TABLES
    if value not in TABLES.keys():
        raise click.BadParameter('Unknown table ({}). Available tables are: {}'
                                 .format(value, TABLES.keys()), param=param)
    return TABLES[value]


# ARGUMENTS
arg_config = click.argument(
    'config',
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

arg_sources = click.argument(
    'sources',
    nargs=-1,
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

def arg_db_table(f):
    from ..db import TABLES
    return click.argument(
        'table',
        type=click.Choice(TABLES.keys()),
        callback=callback_db_table
    )(f)

# OPTIONS
def opt_config_file(f):
    def callback(ctx, param, value):
        ctx.obj = ctx.obj or {}
        ctx.obj['config_file'] = value
        return value
    return click.option('--config', '-C', 'config_file',
                        allow_from_autoenv=True,
                        show_default=True,
                        expose_value=False,
                        callback=callback,
                        type=click.Path(exists=True, dir_okay=False, resolve_path=True),
                        help='Configuration file')(f)

opt_db_filter = click.option(
    '--filter', 'filter_',
    type=str,
    callback=callback_dict,
    multiple=True,
    help='Filter TABLE by attr=value'
)

opt_creation_options = click.option(
    '--co',
    'creation_options',
    metavar='OPTION=VALUE',
    multiple=True,
    default=None,
    show_default=True,
    callback=callback_dict,
    help='Driver creation options')

opt_format = click.option(
    '-of', '--format', 'driver',
    default='GTiff',
    show_default=True,
    help='Output format driver')

opt_nodata = click.option(
    '--ndv',
    type=float,
    default=None,
    show_default=True,
    help='Override source nodata value')

opt_overwrite = click.option(
    '--overwrite',
    is_flag=True,
    help='Overwrite destination file')

def opt_multiprocess_method(f):
    def _callback(ctx, param, value):
        return multiprocess.get_executor(value, ctx.params['njob'])
    return click.option(
        '--parallel',
        type=click.Choice(multiprocess.MULTIPROC_METHODS),
        default='serial',
        callback=_callback,
        help='Method of parallel execution')(f)

opt_multiprocess_njob = click.option(
        '-j', '--njob',
        type=int,
        default=1,
        is_eager=True,
        help='Number of jobs for parallel execution'
    )
