""" Handler for Landsat data processed and distributed through ESPA
"""
import os


class ESPALandsat(object):
    """ ESPA processed "Level 2" Landsat data

    Args:
        path (str): the path to the root directory of the extracted data
            product
    """

    def __init__(self, path):
        self.path = path
