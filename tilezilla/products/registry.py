""" Products available to ingest by this package

.. todo::

    1. We'll need some kind of registry of available products
    2. Products should raise exception if file path provided doesn't look
       like an instance of the product
    3. If product succeeds, put product class on top of test list to avoid
       repeated fails for subsequent ingests (i.e., assume all )
"""
from collections import OrderedDict
import logging

from .espa import ESPALandsat

logger = logging.getLogger('tilezilla')

PRODUCTS = [
    ('ESPALandsat', ESPALandsat)
]


class ProductRegistry(object):
    """ A registry of product types
    """
    def __init__(self, products):
        self.products = OrderedDict(products)
        self._order = range(len(self.products))

    def sniff_product_type(self, path):
        """ Return an initialized product located a given path

        Args:
            path (str): the path to the directory containing the product

        Returns:


        """
        for name in self.products:
            try:
                _product = self.products[name](path)
            except Exception as e:
                logger.debug('{name} could not open {path}: {msg}'
                             .format(name=self.products[name].__name__,
                                     path=path,
                                     msg=str(e)))
            else:
                self.products.insert(0, self.products.pop(name))
                return _product
