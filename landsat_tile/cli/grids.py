import click

_GRIDS = {
    # NLCD 1992: http://webmap.ornl.gov/ogcdown/wcsdown.jsp?dg_id=10009_21
    'nlcd1992': {
        # http://spatialreference.org/ref/sr-org/albers-conical-equal-area-as-used-by-mrlcgov-nlcd/
        'crs': '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs',
        # Spatial Extent: N: 3177735, S: 267885, E: 2266005, W: -2361915
        'bounds': (-2361915.0, 267885.0, 2266005.0, 3177735)
    }
}


def _match_to_grid(input_xy, grid_xy, pix_size):
    """ Return new postings for input that coalign with grid

    Args:
      input_xy (tuple): X/Y coordinate of input extent to be repositioned
      grid_xy (tuple): X/Y coordinate of grid extent to match
      pix_size (tuple): X/Y pixel sizes of data to match

    Returns:
      tuple: new X/Y coordinate of matched input

    """
    new_coords = []
    for grid, _input, ps in zip(grid_xy, input_xy, pix_size):
        offset = int(round((grid - _input) / ps))
        new_coords.append(grid - offset * ps)

    return new_coords


@click.command(
    short_help='Print bounds coordinates for a tile based on a grid')
@click.argument('image', type=click.Path(readable=True, resolve_path=True,
                                         dir_okay=False))
@click.argument('lon', type=float)
@click.argument('lat', type=float)
@click.option('--grid', default=None, type=click.Choice(_GRIDS.keys()),
              help='Use bounds and CRS of a known product')
@click.option('--grid-bounds', nargs=4, type=float, default=None,
              help='Grid bounds: left bottom right top')
@click.option('--grid-crs', default=None,
              help='Grid coordinate reference system.')
@click.pass_context
def tile_bounds(ctx, image, lon, lat, grid, grid_bounds, grid_crs):
    """ Print bounds coordinates for a tile based on a grid
    """

    pass
