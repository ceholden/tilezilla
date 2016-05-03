import os

import click

from .. import multiprocess


def fetch_config(ctx):
    """ Fetch `config_file` from context
    """
    config = ctx.obj and ctx.obj.get('config', None)
    if not config:
        _opts = dict((o.name, o) for o in ctx.parent.command.params)
        raise click.BadParameter('Must specify configuration file',
                                 ctx=ctx.parent, param=_opts['config_file'])
    return config


# CALLBACKS
def callback_dict(ctx, param, value):
    """ Call back for dict style arguments (e.g., KEY=VALUE)
    """
    # TODO: support KEY(operator)VALUE where operator in > >= = <= <
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


def callback_from_stdin(ctx, param, value):
    """ If `value` is empty, try to parse this arg from `stdin`
    """
    if not value:
        stdin = click.get_text_stream('stdin')
        if not stdin:
            _type = ('argument' if isinstance(param, click.core.Argument)
                     else 'option')
            raise click.BadParameter(
                'Must specify parameter via stdin or as {}'.format(_type),
                param=param)

        value = (v.strip('\n ') for v in stdin if v)
        return param.process_value(ctx, value)
    return value


# ARGUMENTS
arg_config = click.argument(
    'config',
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

arg_sources = click.argument(
    'sources',
    nargs=-1,
    type=click.Path(readable=True, resolve_path=True, dir_okay=True))

def arg_db_table(f):
    from ..db import TABLES
    return click.argument(
        'table',
        type=click.Choice(TABLES.keys()),
        callback=callback_db_table
    )(f)

# OPTIONS
opt_config_file = click.option(
    '--config', '-C', 'config_file',
    default=lambda: os.environ.get('TILEZILLA_CONFIG', None),
    allow_from_autoenv=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='Configuration file')

opt_db_filter = click.option(
    '--filter', 'filter_',
    type=str,
    multiple=True,
    help='Filter TABLE by [ATTR][OPERATOR][VALUE...]'
)

opt_db_distinct = click.option(
    '--distinct', type=str, default=None, show_default=True,
    help='Select distinct entries of column specified'
)

opt_db_groupby = click.option(
    '--group_by', type=str, default=None, show_default=True,
    help='Group entries by column specified'
)

opt_db_select = click.option(
    '--select', type=str, default=None, show_default=True, multiple=True,
    help='Print (select) one or more columns'
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
        '--parallel-executor', '-pe',
        'executor',
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
