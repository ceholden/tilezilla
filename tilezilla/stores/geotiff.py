""" GeoTIFF storage method
"""
import os

import rasterio

from .._util import mkdir_p


class GeoTIFFStore(object):
    """ GeoTIFF tile store

    A work in progress...

    The GeoTIFF tile storage method separates individual acquisitions into
    separate sub-directories. For example:

    .. code-block:: bash

        ./
            ./LT50130302009294GNC01/
            ./LT50130292009294GNC01/
            ./LT50120292009303GNC01/
                ./LT50120292009303GNC01_sr_band1.tif
                ./LT50120292009303GNC01_sr_band2.tif
                ...
                ./LT50120292009303GNC01_sr_cfmask.tif

    Args:
        path (str): The root directory where the tile should be stored. The
            path specified should already separate among tiles, if desired.
        tile (Tile): The dataset tile to store
        product (TODO): a product to store

    """

    #: dict: GeoTIFF creation options
    meta_options = {
        'driver': 'GTiff',
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256,
        'compress': 'deflate'
    }

    def __init__(self, path, tile, product):
        self.tile = tile
        self.path = path
        self.product = product
        # Update metadata options with tile details
        self.meta_options.update({
            'affine': tile.affine,
            'transform': tile.affine,
            'width': tile.tilespec.size[0],
            'height': tile.tilespec.size[1]
        })

    def store_variable(self, band, src=None, overwrite=False):
        """ Store product contained within this tile
        """
        _path = os.path.join(self.path, self.product.timeseries_id)
        mkdir_p(_path)
        dst_path = os.path.join(_path, os.path.basename(band.path))

        _src = src or band.src

        dst_meta = _src.meta.copy()
        dst_meta.update(self.meta_options)
        with rasterio.open(dst_path, 'w', **dst_meta) as dst:
            src_window = src.window(*dst.bounds, boundless=True)
            dst.write_band(1, src.read(1, window=src_window, boundless=True))

    def retrieve_variable(self, **kwargs):
        """ Retrieve a product stored within this tile
        """
        pass
