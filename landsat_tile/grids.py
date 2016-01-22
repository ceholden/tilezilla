""" Predefined grids and utilities for working with grid systems
"""
import json
import pkgutil

import rasterio.crs


# Load grid from package data
def retrieve_grids():
    """ Retrieve default grids packaged within ``landsat_tile``

    Returns:
        dict: default grids packaged within ``landsat_tile``
    """
    grids = json.loads(pkgutil.get_data('landsat_tile', 'data/grids.json'))
    for key in grids:
        grids[key]['crs'] = rasterio.crs.from_string(grids[key]['crs'])
    return grids
GRIDS = retrieve_grids()


def create_grid_spec(ul, crs, res):
    """ Creates a grid specification for use in module

    Args:
        ul (iterable): grid upper left x/y coordinate (left top)
        crs (str): grid coordinate reference system
        res (iterable): grid x/y resolution

    Raises:
        ValueError: raise if coordinate reference string could not be parsed
            to a projection

    Returns:
        dict: grid specification, including the ``bounds``, ``crs``, and
            ``res``
    """
    _crs = rasterio.crs.from_string(crs)
    if not _crs:
        raise ValueError('Could not parse coordinate reference system string '
                         'to a projection')

    return {
        'ul': ul,
        'crs': _crs,
        'res': res
    }
