""" GeoTIFF storage method
"""
import os
import shutil

import numpy as np
import rasterio

from .._util import mkdir_p
from ..errors import FillValueException
from ..geoutils import meta_to_bounds


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
        product (BaseProduct): A :class:`tilezilla.product.core.BaseProduct`
            to store
        meta_options (dict): Additional creation options or metadata for
            `rasterio` driver

    """

    #: dict: GeoTIFF creation options
    meta_options = {
        'driver': 'GTiff',
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256,
        'compress': 'deflate'
    }

    def __init__(self, path, tile, product, meta_options=None):
        self.path = path
        self.tile = tile
        self.product = product
        self.meta_options.update(meta_options or {})

        self.meta_options.update({
            'affine': tile.affine,
            'transform': tile.affine,
            'width': tile.tilespec.size[0],
            'height': tile.tilespec.size[1]
        })

        #: str: The directory prefix (dirname) for this product store
        self._dirname = os.path.join(self.path, self.product.timeseries_id)
        mkdir_p(self._dirname)

    def store_variable(self, band, overwrite=False):
        """ Store product contained within this tile

        Args:
            band (Band): A :class:`Band` containing an observed variable
            overwrite (bool): Allow overwriting

        Returns:
            str: The path to the stored variable

        """
        # Ensure source data has observations (i.e., not an edge)
        dst_bounds = meta_to_bounds(**self.meta_options)
        src_window = band.src.window(*dst_bounds, boundless=True)

        src_data = band.src.read(1, window=src_window, boundless=True)
        if np.all(src_data == band.fill):
            raise FillValueException

        dst_path = self._band_filename(band)

        dst_meta = band.src.meta.copy()
        dst_meta.update(self.meta_options)
        with rasterio.open(dst_path, 'w', **dst_meta) as dst:
            dst.write_band(1, src_data)

        return dst_path

    def retrieve_variable(self, **kwargs):
        """ Retrieve a product stored within this tile
        """
        raise NotImplementedError('Reading is less important right now for '
                                  'this driver at the moment as data from'
                                  'it can be read directly from disk.')

    def store_file(self, path):
        """ Store a file with the product in an accessible way

        An example use case for this method include storing metadata files
        associated with a given product (e.g., "MTL" text files for Landsat).

        Args:
            path (str): The path of the file to be stored

        Returns:
            str: The path of the file once copied into this product's store
        """
        return shutil.copy(path, self._dirname)

    def _band_filename(self, band):
        """ Return full filename for a given band
        """
        return os.path.join(self._dirname, os.path.basename(band.path))
