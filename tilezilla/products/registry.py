""" Products available to ingest by this package
"""
from collections import OrderedDict
import logging

from .espa import ESPALandsat

logger = logging.getLogger('tilezilla')

PRODUCTS = [
    (ESPALandsat.description, ESPALandsat)
]


class ProductRegistry(object):
    """ A registry of product types
    """
    def __init__(self, products):
        self.products = OrderedDict(products)
        self._order = [k for k in self.products.keys()]

    def sniff_product_type(self, path):
        """ Return an initialized product located a given path

        Args:
            path (str): the path to the directory containing the product

        Returns:
            object: a product to work with
        """
        for name in self._order:
            try:
                _product = self.products[name].from_path(path)
            except Exception as e:
                logger.debug('{name} could not open {path}: {msg}'
                             .format(name=self.products[name].__name__,
                                     path=path,
                                     msg=str(e)))
            else:
                self._order.insert(0, name)
                return _product
