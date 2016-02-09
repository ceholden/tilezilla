""" Handler for Landsat data processed and distributed through ESPA
"""
import os


class ESPALandsat(object):
    """ ESPA processed Landsat data

    Args:
        dirpath (str):
    """

    def __init__(self, dirpath):
        self.dirpath = dirpath
