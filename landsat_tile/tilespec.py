""" Predefined tile specifications and utilities for working with tile systems
"""
import itertools
import json
import pkgutil

import rasterio.crs
import rasterio

from . import geoutils
from .core import BoundingBox


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

    def index_to_tile_bounds(self, index):
        """ Return tile footprint bounds for given index

        Args:
            index (tuple): tile x/y index

        Returns:
            BoundingBox: the :attr:`BoundingBox` of a tile
        """

        return BoundingBox(
            left=self.ul[0] + index[0] * self.size[0] * self.res[0],
            right=self.ul[0] + (index[0] + 1) * self.size[0] * self.res[0],
            top=self.ul[1] - index[1] * self.size[1] * self.res[1],
            bottom=self.ul[1] - (index[1] + 1) * self.size[1] * self.res[1]
        )

    def bounds_to_tile_bounds(self, bounds):
        """ Yield the tile footprints for this tile spec intersecting a bounds

        .. note::

            It is required that the input ``bounds`` be in the same
            coordinate reference system as :paramref:`crs <.TileSpec.crs>`.

        Args:
            bounds (rasterio.coords.BoundingBox): input bounds

        Yields:
            rasterio.coords.BoundingBox: boundaries for each tile

        """
        grid_xs, grid_ys = self._frame_bounds(bounds)
        for tile_index in itertools.product(grid_xs, grid_ys):
            tile_bounds = self.index_to_tile_bounds(tile_index)
            if geoutils.intersects_bounds(bounds, tile_bounds):
                yield tile_bounds

    def _frame_bounds(self, bounds):
        min_grid_x = (self.ul[0] - bounds.left) // self.size[0]
        max_grid_x = (self.ul[0] - bounds.right) // self.size[0]
        min_grid_y = (self.ul[1] - bounds.top) // self.size[1]
        max_grid_y = (self.ul[1] - bounds.bottom) // self.size[1]
        return (range(int(min_grid_x), int(max_grid_x) + 1),
                range(int(min_grid_y), int(max_grid_y) + 1))
