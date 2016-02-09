""" Classes, functions, etc. core to the module
"""
import rasterio


class Band(object):
    """ Basically just a rasterio dataset with extra metadata

    Args:

    """
    def __init__(self, filename):
        with rasterio.drivers():
            self.src = rasterio.open(filename)
