""" Core baseclass for products in ``tilezilla``

Defines the class attributes and methods required for a product.
"""
import abc
import textwrap

import six


class BaseProduct(six.with_metaclass(abc.ABCMeta)):
    """ Product interface for ``tilezilla``

    Args:
        path (str): the path to the root directory of the extracted data
            product
        bands (list[Band]): List of :class:`Band` for this dataset
        metadata (dict): Dictionary of metadata about this product
    """

    def __repr__(self):
        s = """
        Product: {desc}

        Scene ID: {scene_id}
        Acquisition date/time: {acquired}
        Processing date/time: {processed}
        Bounding Box:
            Top:        {uly}
            Left:       {ulx}
            Bottom:     {lry}
            Right:      {lrx}

        Bands: {nbands}
        {band_names}
        """.format(
            desc=self.description,
            scene_id=self.timeseries_id,
            acquired=self.acquired.datetime,
            processed=self.processed.datetime,
            uly=self.bounds.top,
            ulx=self.bounds.left,
            lry=self.bounds.bottom,
            lrx=self.bounds.right,
            nbands=len(self.bands),
            band_names='\n'.join(
                [''] + [' ' * 12 + b.long_name for b in self.bands])
        )
        return textwrap.dedent(s)

    @classmethod
    @abc.abstractmethod
    def from_path(cls, path):
        """ Return an instance of this product stored at a given path
        """
        pass

    @abc.abstractproperty
    def description(self):
        """ str: Description of product
        """
        return

    @abc.abstractproperty
    def bands(self):
        """ list[:class:`Band`]: bands contained within dataset
        """
        return

    @abc.abstractproperty
    def timeseries_id(self):
        """ str: identifier for this acquisition
        """
        pass

    @abc.abstractproperty
    def acquired(self):
        """ Arrow: date and time of acquisition
        """
        return

    @abc.abstractproperty
    def processed(self):
        """ Arrow: Date and time of processing
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
    def bounds(self):
        """ BoundingBox: The bounding box of this product in EPSG:4326
        """
        return

    @abc.abstractproperty
    def metadata(self):
        """ dict: Dictionary of metadata about this product
        """
        return

    @abc.abstractproperty
    def metadata_files(self):
        """ dict: name and paths to any metadata files for this observation
        """
        return
