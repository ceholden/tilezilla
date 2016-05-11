""" Core baseclass for products in ``tilezilla``

Defines the class attributes and methods required for a product.
"""
import abc
import textwrap

import six



@six.add_metaclass(abc.ABCMeta)
class BaseProduct(object):
    """ Product interface for ``tilezilla``

    Attributes:
        description (str): Description of the collection this product belongs
            to (e.g., ESPALandsat, MODIS_C6)

    Args:
        timeseries_id (str): Unique acquisition ID
        acquired (datetime): Acquisition date and time
        processed (datetime): Product processing date and time
        platform (str): Satellite / aircraft platform (e.g., AQUA)
        instrument (str): Remotely sensed instrument (e.g., MODIS)
        bounds (BoundingBox): A rough estimate of the bounding box for this
            product acquisition. Bounds are used as an initial guess for the
            tiles that intersect this product, so it is more important that
            this box encloses the actual product bounds than it is to be very
            accurate
        bands (list[Band]): List of :class:`Band` for this dataset
        metadata (dict): Dictionary of metadata about this product
        metadata_files (list[str]): List of filenames containing ancillary
            metadata
    """

    def __init__(self, timeseries_id,
                 acquired, processed, platform, instrument, bounds,
                 bands=None, metadata=None, metadata_files=None):
        self.timeseries_id = timeseries_id
        self.acquired = acquired
        self.processed = processed
        self.platform = platform
        self.instrument = instrument
        self.bounds = bounds

        self.bands = bands or []
        self.metadata = metadata or {}
        self.metadata_files = metadata_files or {}

    def __repr__(self):
        s = """
        Product: {0.description}

        Scene ID: {0.timeseries_id}
        Acquisition date/time: {acquired}
        Processing date/time: {processed}
        Bounding Box:
            Top:        {bounds.top}
            Left:       {bounds.left}
            Bottom:     {bounds.bottom}
            Right:      {bounds.right}

        Bands: {nbands}
        {band_names}
        """.format(self,
                   acquired=self.acquired.datetime,
                   processed=self.processed.datetime,
                   bounds=self.bounds,
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
        raise NotImplementedError

    def bands(self):
        """ list[:class:`Band`]: bands contained within dataset
        """
        raise NotImplementedError

    def timeseries_id(self):
        """ str: identifier for this acquisition
        """
        raise NotImplementedError

    def acquired(self):
        """ Arrow: date and time of acquisition
        """
        raise NotImplementedError

    def processed(self):
        """ Arrow: Date and time of processing
        """
        raise NotImplementedError

    def platform(self):
        """ str: the platform holding the sensor instrument of this acquisition
        """
        raise NotImplementedError

    def instrument(self):
        """ str: the instrument sensor of this acquisition
        """
        raise NotImplementedError

    def bounds(self):
        """ BoundingBox: The bounding box of this product in EPSG:4326
        """
        raise NotImplementedError

    def metadata(self):
        """ dict: Dictionary of metadata about this product
        """
        raise NotImplementedError

    def metadata_files(self):
        """ dict: name and paths to any metadata files for this observation
        """
        raise NotImplementedError
