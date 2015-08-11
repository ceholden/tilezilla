""" Predefined grids and utilities for working with grid systems
"""
import shapely.geometry

# TODO: move this to a json file (?)
# Grids are defined as a dictionary of projection / geotransform parameters
# listed in the style of `rasterio`
grids = {
    # NLCD 1992: http://webmap.ornl.gov/ogcdown/wcsdown.jsp?dg_id=10009_21
    'nlcd1992': {
        # http://spatialreference.org/ref/sr-org/albers-conical-equal-area-as-used-by-mrlcgov-nlcd/
        # 'crs': '+proj=aea +lat_0=23 +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs',
        'crs': '+ellps=GRS80 +lat_0=23 +lat_1=29.5 +lat_2=45.5 +lon_0=-96 +no_defs +proj=aea +towgs84=0,0,0,0,0,0,0 +units=m +x_0=0 +y_0=0',
        # Spatial Extent: N: 3177735, S: 267885, E: 2266005, W: -2361915
        'bounds': [-2361915.0, 267885.0, 2266005.0, 3177735],
        'res': [30, 30]
    }
}


def match_to_grid(match, grid, pix_size):
    """ Return new postings for input that coalign with grid

    Args:
      match (iterable): X or Y coordinates of input extent to be repositioned
      grid_xy (iterable): X or Y coordinates of grid extent to match
      pix_size (iterable): X or Y pixel sizes of data to match

    Returns:
      tuple: new X/Y coordinate of matched input

    """
    new_coords = []

    for _grid, _match, ps in zip(grid, match, pix_size):
        offset = int(round((_grid - _match) / ps))
        new_coords.append(_grid - offset * ps)

    return new_coords


def intersects_bounds(a_bounds, b_bounds):
    """ Return True/False if a intersects b

    Args:
      a_bounds (iterable): bounds of a (left bottom right top)
      b_bounds (iterable): bounds of b (left bottom right top)

    Returns:
      bool: True/False if a intersects b

    """
    a = bounds_to_polygon(a_bounds)
    b = bounds_to_polygon(b_bounds)

    return a.intersects(b)


def bounds_to_polygon(bounds):
    """ Returns Shapely polygon of bounds

    Args:
      bounds (iterable): bounds (left bottom right top)

    Returns:
      shapely.geometry.Polygon: polygon of bounds

    """
    return shapely.geometry.Polygon([
        (bounds[0], bounds[1]),
        (bounds[2], bounds[1]),
        (bounds[2], bounds[3]),
        (bounds[0], bounds[3])
    ])
