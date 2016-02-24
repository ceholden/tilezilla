""" Core baseclass for products in ``tilezilla``

Defines the class attributes and methods required for a product.
"""
import abc


class BaseProduct(object):
    """ Product interface for ``tilezilla``

    Args:
        path (str): the path to the root directory of the extracted data
            product
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, path):
        self.path = path

    @abc.abstractproperty
    def bands(self):
        """ list[:class:`Band`]: bands contained within dataset
        """
        return

    @abc.abstractproperty
    def timeseries_id(self):
        """ str: identifier for this acquisition
        """
        return

    @abc.abstractproperty
    def time(self):
        """ Arrow: date and time of acquisition
        """
        return

    @abc.abstractproperty
    def platform(self):
        """ str: the platform holding the sensor instrument of this acquisition
        """
        return

    @abc.abstractproperty
    def instrument(self):
        """ str: the instrument sensor of this acquisition
        """
        return

    @abc.abstractproperty
    def metadata_files(self):
        """ dict: name and paths to any metadata files for this observation
        """
        return

    @abc.abstractmethod
    def bounding_box(self, crs='EPSG:4326'):
        """ Return the bounding box of this product in some projection

        Args:
            crs (str or dict): The coordinate reference system, interpretable
                by rasterio

        Returns:
            BoundingBox: bounding box of product
        """
        return
