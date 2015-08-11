import re

import click


# CALLBACKS
def callback_lnglat(ctx, param, value):
    """ Convert coordinates with N/S/W/E coordinates into numbers
    """
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


# ARGUMENTS
arg_source = click.argument('source', metavar='INPUT',
                            type=click.Path(readable=True, resolve_path=True,
                                            dir_okay=False))

arg_destination = click.argument('destination', metavar='OUTPUT',
                                 type=click.Path(writable=True,
                                                 resolve_path=True))

# OPTIONS
opt_longitude = click.argument('lon', callback=callback_lnglat)

opt_latitude = click.argument('lat', callback=callback_lnglat)

opt_format = click.option('-of', '--format', 'driver',
                          default='GTiff', show_default=True,
                          help='Output format driver')
