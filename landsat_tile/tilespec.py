""" Predefined tile specifications and utilities for working with tile systems
"""
import json
import pkgutil

import rasterio.crs
import rasterio


# Load tile specifications from package data
def retrieve_tilespecs():
    """ Retrieve default tile specifications packaged within ``landsat_tile``

    Returns:
        dict: default tilespecs packaged within ``landsat_tile``
    """
    tilespecs = json.loads(pkgutil.get_data('landsat_tile',
                                            'data/tile_specs.json').decode())
    for key in tilespecs:
        tilespecs[key]['crs'] = rasterio.crs.from_string(tilespecs[key]['crs'])
    return tilespecs
TILESPECS = retrieve_tilespecs()


class TileSpec(object):
    """ Tile specification object representation

    Args:
        ul (tuple): upper left X/Y coordinates
        crs (str): coordinate system reference string
        res (tuple): pixel X/Y resolution
        size (tuple): number of pixels in X/Y dimension of each tile
    """
    def __init__(self, ul, crs, res, size):
        self.ul = ul
        self.crs = crs
        self.res = res
        self.size = size
        if not self.crs:
            raise ValueError('Could not parse coordinate reference system '
                             'string to a projection ({})'.format(crs))

    def bounds_to_tiles(self, bounds):
        """ Yield the tile footprints for this tile spec intersecting a bounds

        .. note::

            It is required that the input ``bounds`` be in the same
            coordinate reference system as :paramref:`crs <.TileSpec.crs>`.

        Args:
            bounds (rasterio.coords.BoundingBox): input bounds

        Yields:
            rasterio.coords.BoundingBox: boundaries for each tile

        """
        pass
