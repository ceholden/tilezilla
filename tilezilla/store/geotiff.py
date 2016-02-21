""" GeoTIFF storage method
"""
import os


class GeoTIFFStore(object):
    """ GeoTIFF tile store

    A work in progress...

    The GeoTIFF tile storage method separates individual acquisitions into
    separate sub-directories. For example::

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
        tile (Tile): The dataset tile to store
        path (str): The root directory where the tile should be stored. The
            path specified should already separate among tiles, if desired.

    """
    def __init__(self, tile, path):
        self.tile = tile

    def store(self, product):
        """ Store product contained within this tile
        """
        pass

    def retrieve(self, **kwargs):
        """ Retrieve a product stored within this tile
        """
        pass
