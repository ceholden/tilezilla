""" Classes, functions, etc. core to the module
"""
from collections import namedtuple

import rasterio


#: easy access container for a bounding box
BoundingBox = namedtuple('BoundingBox', ('left', 'bottom', 'right', 'top'))


class Band(object):
    """ Basically just a rasterio dataset with extra metadata

    Basically just benefit from composition by sitting on top of ``rasterio``
    over re-implementing any related methods.

    Args:
        filename (str): the filename of the raster image to use
        bidx (int): 1-indexed band from within the dataset to use

    """
    def __init__(self, filename, bidx=1):
        with rasterio.drivers():
            #: the GDAL dataset opened with rasterio
            self.src = rasterio.open(filename)
            #: the GDAL band from ``self.src`` opened with rasterio
            self.band = rasterio.band(self.src, bidx)
