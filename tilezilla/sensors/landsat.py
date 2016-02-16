""" Module for dealing with Landsat sensors
"""
from collections import OrderedDict

from .._util import dict_keymap_get, dict_keymap_set, lazy_property


def parse_MTL(path):
    """ Return a nested, ordered dict from a Landsat "MTL" metadata file

    Args:
        path (str): MTL filename

    Returns:
        OrderedDict: nested dict of MTL file
    """
    data = OrderedDict()
    with open(path, 'r') as fid:
        inner_keys = []
        for line in fid:
            if '=' in line:
                k, v = (i.strip().strip('"')
                        for i in line.strip().split('='))
                if k == 'GROUP':
                    if inner_keys:
                        dict_keymap_set(data, inner_keys, v, OrderedDict())
                    else:
                        data[v] = OrderedDict()
                    inner_keys.append(v)
                elif k == 'END_GROUP':
                    inner_keys.pop(-1)
                elif inner_keys:
                    dict_keymap_set(data, inner_keys, k, v)
    return data


class MTL(object):
    """ Landsat "MTL" metadata file

    Args:
        path (str): path to the MTL file
    """

    def __init__(self, path):
        #: OrderedDict: metadata contained within the MTL file
        self.data = parse_MTL(path)['L1_METADATA_FILE']

    @lazy_property
    def scene_id(self):
        """ Landsat scene ID (e.g., LT50120312002300LGS01)
        """
        return dict_keymap_get(self.data,
                               ['METADATA_FILE_INFO', 'LANDSAT_SCENE_ID'])

    @lazy_property
    def LPGS(self):
        """ Level-1 Product Generation System version number
        """
        return dict_keymap_get(self.data, ['METADATA_FILE_INFO',
                                           'PROCESSING_SOFTWARE_VERSION'])

    @lazy_property
    def product_level(self):
        """ Level-1 product level (L1G, L1T, etc.)
        """
        return dict_keymap_get(self.data, ['PRODUCT_METADATA', 'DATA_TYPE'])

    @lazy_property
    def sensor(self):
        """ Landsat sensor (e.g., LT4, LT5)
        """
        return dict_keymap_get(self.data, ['PRODUCT_METADATA',
                                           'SPACECRAFT_ID'])

    @lazy_property
    def path_row(self):
        """ WRS-2 path and row
        """
        path = dict_keymap_get(self.data, ['PRODUCT_METADATA', 'WRS_PATH'])
        row = dict_keymap_get(self.data, ['PRODUCT_METADATA', 'WRS_ROW'])
        return path, row

    @lazy_property
    def cloud_cover(self):
        """ ACCA cloud cover score
        """
        return float(dict_keymap_get(self.data,
                                     ['IMAGE_ATTRIBUTES', 'CLOUD_COVER']))
