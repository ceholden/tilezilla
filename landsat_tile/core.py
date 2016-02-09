""" Classes, functions, etc. core to the module
"""
from collections import namedtuple

import rasterio


#: easy access container for a bounding box
BoundingBox = namedtuple('BoundingBox', ('left', 'bottom', 'right', 'top'))


class Band(object):
    """ Basically just a rasterio dataset with extra metadata

    Args:

    """
    def __init__(self, filename):
        with rasterio.drivers():
            self.src = rasterio.open(filename)
