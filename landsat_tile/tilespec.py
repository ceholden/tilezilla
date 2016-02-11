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
    """ A tile specification or tile scheme

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

    def __getitem__(self, index):
        """ Return a Tile for the grid row/column specified by index
        """
        if isinstance(index, tuple):
            if len(index) > 2:
                raise IndexError('TileSpec only has two dimensions (row/col)')
            # _row, _col = [], []
            if not isinstance(index[0], int) and isinstance(index[1], int):
                raise NotImplementedError(
                    'Only support indexing int/int for now')
            return self.index_to_tile_bounds((index[1], index[0]))

    def _index_to_bounds(self, index):
        """ Return Tile footprint bounds for given index

        Args:
            index (tuple): tile row/column index

        Returns:
            BoundingBox: the :attr:`BoundingBox` of a tile
        """
        return BoundingBox(
            left=self.ul[0] + index[1] * self.size[0] * self.res[0],
            right=self.ul[0] + (index[1] + 1) * self.size[0] * self.res[0],
            top=self.ul[1] - index[0] * self.size[1] * self.res[1],
            bottom=self.ul[1] - (index[0] + 1) * self.size[1] * self.res[1]
        )

    def _index_to_tile(self, index):
        """ Return the Tile for given index

        Args:
            index (tuple): tile row/column index

        Returns:
            Tile: a Tile object
        """
        if index not in self._tiles:
            bounds = self._index_to_bounds(index)
            self._tiles[index[1], index[0]] = Tile(bounds, self.crs)
        return self._tiles[index]

    def bounds_to_tile(self, bounds):
        """ Yield Tile objects for this TileSpec that intersect a given bounds

        .. note::

            It is required that the input ``bounds`` be in the same
            coordinate reference system as :paramref:`crs <.TileSpec.crs>`.

        Args:
            bounds (BoundingBox): input bounds

        Yields:
            Tile: the Tiles that intersect within a bounds
        """
        grid_ys, grid_xs = self._frame_bounds(bounds)
        for index in itertools.product(grid_ys, grid_xs):
            tile = self._index_to_tile(index)
            if geoutils.intersects_bounds(bounds, tile.bounds):
                yield tile

    def _frame_bounds(self, bounds):
        min_grid_x = (self.ul[0] - bounds.left) // self.size[0]
        max_grid_x = (self.ul[0] - bounds.right) // self.size[0]
        min_grid_y = (self.ul[1] - bounds.top) // self.size[1]
        max_grid_y = (self.ul[1] - bounds.bottom) // self.size[1]
        return (range(int(min_grid_y), int(max_grid_y) + 1),
                range(int(min_grid_x), int(max_grid_x) + 1))


class Tile(object):
    """ A tile

    Args:
        bounds (BoundingBox): the bounding box of the tile
        crs (str): the coordinate reference system of the tile

    """
    def __init__(self, bounds, crs):
        self.bounds = bounds
        self.crs = crs

    @property
    def geom_geojson(self):
        """ Tile geometry in GeoJSON format
        """
        geojson = """
        {
            "geometry":
            {
                "coordinates": [[
                    [{top}, {left}],
                    [{top}, {right}],
                    [{bottom}, {right}],
                    [{bottom}, {left}],
                    [{top}, {left}]
                ]],
                "type": "Polygon"
            }
        }
        """.format(**self.bounds._asdict())
        return json.loads(geojson)
