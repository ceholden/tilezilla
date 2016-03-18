import functools
import re

import click


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


def callback_lnglat(ctx, param, value):
    """ Convert coordinates with N/S/W/E coordinates into numbers
    """
    if not value:
        return None

    def _process_coord(param, value):
        # Input should look like 70W, 10N, 10S, 70E, etc.
        mag_dir = re.findall('\d+|\D+', value)
        # Cardinal direction and coordinate should fall into [0] or [1]
        if len(mag_dir) < 2:
            raise click.BadParameter(
                'Could not parse input lon/lat coordinate',
                param=param.name, param_hint=value)
        try:
            magnitude = float(mag_dir[0])
        except:
            try:
                magnitude = float(mag_dir[1])
            except ValueError:
                raise click.BadParameter(
                    'Could not parse input lon/lat coordinate',
                    param=param.name, param_hint=value)
            else:
                direction = mag_dir[0].strip()
        else:
            direction = mag_dir[1].strip()
        finally:
            direction = 1 if direction.upper() in ('N', 'E') else -1

        return magnitude * direction

    coords = []
    for coord in value:
        coords.append(_process_coord(param, coord))

    return tuple(coords)


# ARGUMENTS
arg_config = click.argument(
    'config',
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

arg_sources = click.argument(
    'sources',
    nargs=-1,
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

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

opt_longitude = click.option(
    '--lon',
    metavar='#[W|E]',
    default=None,
    multiple=True,
    show_default=True,
    callback=callback_lnglat,
    help='Only process tile that intersects this longitude')

opt_latitude = click.option(
    '--lat',
    metavar='#[N|S]',
    default=None,
    multiple=True,
    callback=callback_lnglat,
    help='Only process tile that intersects this latitude')

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
