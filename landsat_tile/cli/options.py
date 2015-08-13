import re

import click


# CALLBACKS
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
arg_source = click.argument(
    'source',
    metavar='INPUT',
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

arg_sources = click.argument(
    'sources',
    nargs=-1,
    metavar='INPUTS...',
    type=click.Path(readable=True, resolve_path=True, dir_okay=False))

arg_tile_dir = click.argument(
    'tile_dir',
    nargs=1,
    metavar='TILE_DIR',
    type=click.Path(writable=True, file_okay=False, resolve_path=True))

# OPTIONS
opt_longitude = click.option(
    '--lon',
    metavar='#[W|E]',
    default=None,
    multiple=True,
    show_default=True,
    callback=callback_lnglat,
    help='Override upper left longitude of tile')

opt_latitude = click.option(
    '--lat',
    metavar='#[N|S]',
    default=None,
    multiple=True,
    callback=callback_lnglat,
    help='Override upper left latitude of tile')

opt_format = click.option(
    '-of', '--format', 'driver',
    default='GTiff',
    show_default=True,
    help='Output format driver')

opt_overwrite = click.option(
    '--overwrite',
    is_flag=True,
    help='Overwrite destination file')
