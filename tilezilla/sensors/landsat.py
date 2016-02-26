""" Module for dealing with Landsat sensors
"""
from collections import OrderedDict

from .._util import lazy_property


def parse_MTL(fid):
    """ Return an ordered dict from a Landsat "MTL" metadata file

    Args:
        fid (file descriptor): file descriptor for "MTL" metadata file

    Returns:
        OrderedDict: dict of MTL file
    """
    data = OrderedDict()
    for line in fid:
        split = line.decode().split(' = ')
        if len(split) == 2:
            data[split[0].strip().strip('"')] = split[1].strip().strip('"')
    return data


class MTL(object):
    """ Landsat "MTL" metadata file

    Args:
        data (OrderedDict): metadata contained within the MTL file
    """
    def __init__(self, data):
        self.data = data

    @lazy_property
    def scene_id(self):
        """ Landsat scene ID (e.g., LT50120312002300LGS01)
        """
        return self.data['LANDSAT_SCENE_ID']

    @lazy_property
    def LPGS(self):
        """ Level-1 Product Generation System version number
        """
        return self.data['PROCESSING_SOFTWARE_VERSION']

    @lazy_property
    def product_level(self):
        """ Level-1 product level (L1G, L1T, etc.)
        """
        return self.data['DATA_TYPE']

    @lazy_property
    def sensor(self):
        """ Landsat sensor (e.g., LT4, LT5)
        """
        return self.data['SPACECRAFT_ID']

    @lazy_property
    def path_row(self):
        """ WRS-2 path and row
        """
        path = self.data['WRS_PATH']
        row = self.data['WRS_ROW']
        return path, row

    @lazy_property
    def cloud_cover(self):
        """ ACCA cloud cover score
        """
        return float(self.data['CLOUD_COVER'])

    @classmethod
    def from_file(cls, path):
        """
        Args:
            path (str): path to the MTL file

        Returns:
            MTL: Instance of MTL
        """
        with open(path, 'r') as fid:
            return cls(parse_MTL(fid))

    @classmethod
    def from_fid(cls, fid):
        """
        Args:
            fid (file descriptor): file descriptor for "MTL" metadata file

        Returns:
            MTL: Instance of MTL
        """
        return cls(parse_MTL(fid))
