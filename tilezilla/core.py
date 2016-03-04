""" Classes, functions, etc. core to the module
"""
from collections import namedtuple

import numpy as np
import rasterio

from ._util import lazy_property

#: easy access container for a bounding box
BoundingBox = namedtuple('BoundingBox', ('left', 'bottom', 'right', 'top'))


class Band(object):
    """ Basically just a rasterio dataset with extra metadata

    Basically just benefit from composition by sitting on top of ``rasterio``
    over re-implementing any related methods.

    Metadata will, when relevant, try to follow the variable names suggested
    by the NetCDF Climate and Forecast (CF) Metadata Conventions.

    Args:
        path (str): the path of the raster image to use
        bidx (int): 1-indexed band from within the dataset to use
        standard_name (str): a standard name that references a description
            of the variable
        long_name (str): a descriptive, but not standardized, description of
            the variable
        friendly_name (str): a cross-sensor friendly name to refer to (e.g.,
            'blue' instead of band1)
        units (str): unit of variable
        fill (int or float): fill value for NoData or NaN
        valid_min (int or float): smallest valid value of band data
        valid_max (int or float): largest valid value of band data
        scale_factor (int or float): if present, data will be scaled by this
            number

    """
    def __init__(self, path, bidx=1,
                 standard_name='', long_name='', friendly_name='',
                 units='', fill=np.nan,
                 valid_min=None, valid_max=None, scale_factor=1):
        self.path = path
        self.bidx = bidx
        self.standard_name = standard_name
        self.long_name = long_name
        self.friendly_name = friendly_name
        self.units = units
        self.fill = fill
        self.valid_min = valid_min
        self.valid_max = valid_max
        self.scale_factor = scale_factor

    @lazy_property
    def src(self):
        """ rasterio._io.RasterReader: the Band dataset opened with rasterio
        """
        with rasterio.drivers():
            src = rasterio.open(self.path)

        return src

    @lazy_property
    def band(self):
        """ rasterio.Band: The band from ``self.src`` opened with rasterio
        """
        band = rasterio.band(self.src, self.bidx)
        # TODO: remove?
        # Update min/max values if left None
        info = np.iinfo if band.dtype[0] in ('u', 'i') else np.finfo
        if self.valid_min is None:
            self.valid_min = info(np.dtype(band.dtype)).min
        if self.valid_max is None:
            self.valid_max = info(np.dtype(band.dtype)).max

        return band
