""" Products available to ingest by this package
"""
from collections import OrderedDict
import logging

from .espa import ESPALandsat
from ..errors import ProductNotFoundException

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

        Raises:
            ProductNotFoundException: Raise if product cannot be opened
        """
        found = False
        messages = []
        for name in self._order:
            try:
                _product = self.products[name].from_path(path)
            except Exception as e:
                msg = '{name} could not open {path}: {msg}'.format(
                    name=self.products[name].__name__, path=path, msg=str(e))
                messages.append(msg)
                logger.debug(msg)
            else:
                self._order.insert(0, name)
                found = True
                return _product
        if not found:
            raise ProductNotFoundException(
                'Could not read source as a product. Exceptions include: {}'
                .format('\n'.join(['"{}"'.format(m) for m in messages])))
