""" Predefined tile specifications and utilities for working with tile systems
"""
import itertools
import json
import pkgutil

import rasterio.crs
import rasterio

from . import geoutils
from .core import BoundingBox


class TileSpec(object):
    """ A tile specification or tile scheme

    Args:
        ul (tuple): upper left X/Y coordinates
        crs (str): coordinate system reference string
        res (tuple): pixel X/Y resolution
        size (tuple): number of pixels in X/Y dimension of each tile
        desc (str): description of tile specification (default: None)
    """

    def __init__(self, ul, crs, res, size, desc=None):
        self.ul = ul
        self.crs = crs
        self.res = res
        self.size = size
        if not self.crs:
            raise ValueError('Could not parse coordinate reference system '
                             'string to a projection ({})'.format(crs))
        self.desc = desc or 'unnamed'
        self._tiles = {}

    def __repr__(self):
        return ("<{name}(desc={desc}, ul={ul}, crs={crs}, "
                "res={res}, size={size}) at {hex}>".format(
                    name=self.__class__.__name__,
                    hex=hex(id(self)),
                    desc=self.desc,
                    ul=self.ul,
                    crs=self.crs,
                    res=self.res,
                    size=self.size))

    def __getitem__(self, index):
        """ Return a Tile for the grid row/column specified by index
        """
        if isinstance(index, tuple):
            if len(index) > 2:
                raise IndexError('TileSpec only has two dimensions (row/col)')
            if not isinstance(index[0], int) and isinstance(index[1], int):
                raise NotImplementedError(
                    'Only support indexing int/int for now')
            return self._index_to_tile(index)

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
            bottom=self.ul[1] - (index[0] + 1) * self.size[1] * self.res[1])

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
        min_grid_x = int((self.ul[0] - bounds.left) // self.size[0])
        max_grid_x = int((self.ul[0] - bounds.right) // self.size[0])
        min_grid_y = int((self.ul[1] - bounds.top) // self.size[1])
        max_grid_y = int((self.ul[1] - bounds.bottom) // self.size[1])
        return (range(min_grid_y, max_grid_y + 1),
                range(min_grid_x, max_grid_x + 1))


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
        {{
            "geometry":
            {{
                "coordinates": [[
                    [{top}, {left}],
                    [{top}, {right}],
                    [{bottom}, {right}],
                    [{bottom}, {left}],
                    [{top}, {left}]
                ]],
                "type": "Polygon"
            }}
        }}
        """.format(**self.bounds._asdict())
        return json.loads(geojson)


# Load tile specifications from package data
def retrieve_tilespecs():
    """ Retrieve default tile specifications packaged within ``tilezilla``

    Returns:
        dict: default tilespecs packaged within ``tilezilla`` as TileSpec
            objects
    """
    tilespecs = json.loads(pkgutil.get_data('tilezilla',
                                            'data/tile_specs.json').decode())
    for key in tilespecs:
        tilespecs[key]['crs'] = rasterio.crs.from_string(tilespecs[key]['crs'])
        tilespecs[key] = TileSpec(desc=key, **tilespecs[key])
    return tilespecs

#: dict: Built-in tile specifications available by default
TILESPECS = retrieve_tilespecs()
