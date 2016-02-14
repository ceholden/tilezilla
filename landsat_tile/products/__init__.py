""" Products available to ingest by this package

.. todo::

    1. We'll need some kind of registry of available products
    2. Products should raise exception if file path provided doesn't look
       like an instance of the product
    3. If product succeeds, put product class on top of test list to avoid
       repeated fails for subsequent ingests (i.e., assume all )
"""
from collections import OrderedDict

from .espa import ESPALandsat

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
        pass


#: ProductRegistry: registry of product types usable within this package
registry = ProductRegistry(PRODUCTS)
