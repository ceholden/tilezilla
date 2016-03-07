""" Handler for Landsat data processed and distributed through ESPA
"""
import pathlib

from .._util import find_in_path
from ..sensors.landsat import MTL, ESPAMetadata
from .core import BaseProduct
from ..core import BoundingBox


class ESPALandsat(BaseProduct):
    """ ESPA processed "Level 2" Landsat data
    """
    xml_pattern = 'L*.xml'
    mtl_pattern = 'L*_MTL.txt'

    description = 'ESPALandsat'
    path, timeseries_id, platform, instrument = '', '', '', ''
    acquired, processed = None, None
    bounds = BoundingBox(0, 0, 0, 0)
    bands = []
    metadata, metadata_files = {}, {}

    def __init__(self, path, description,
                 timeseries_id, acquired, processed, platform, instrument,
                 bounds, bands=None, metadata=None, metadata_files=None):
        self.path = pathlib.Path(str(path)).resolve()
        self.description = description
        self.timeseries_id = timeseries_id
        self.acquired = acquired
        self.processed = processed
        self.platform = platform
        self.instrument = instrument
        self.bounds = bounds

        self.bands = bands or []
        self.metadata = metadata or {}
        self.metadata_files = metadata_files or {}

    @classmethod
    def from_path(cls, path):
        """ Return an instance of ESPALandsat stored at a given `path`

        Args:
            path (str): the path to the root directory of the extracted data
                product
        Raises:
            IOError: raise if MTL or ESPA product metadata cannot be found
        """
        mtl_file = find_in_path(path, cls.mtl_pattern)
        if not mtl_file:
            raise IOError('Cannot find MTL metadata file in {}'.format(path))
        if len(mtl_file) > 1:
            raise IOError('Found multiple files matching MTL file search '
                          'pattern ({}): {}'
                          .format(cls.mtl_pattern, mtl_file))

        xml_file = find_in_path(path, cls.xml_pattern)
        if not xml_file:
            raise IOError('Cannot find ESPA XML metadata file in {}'
                          .format(path))
        if len(xml_file) > 1:
            raise IOError('Found multiple files matching ESPA XML file search '
                          'pattern ({}):'.format(cls.xml_pattern, xml_file))

        md_files = dict(MTL=str(mtl_file[0]),
                        ESPAMetadata=str(xml_file[0]))
        mtl = MTL.from_file(md_files['MTL'])
        xml = ESPAMetadata.from_file(md_files['ESPAMetadata'])

        return cls(
            path, cls.description,
            timeseries_id=mtl.scene_id,
            acquired=xml.acquired, processed=xml.processed,
            platform=xml.platform, instrument=xml.instrument,
            bounds=xml.bounds,
            bands=list(xml.bands), metadata=mtl.data, metadata_files=md_files
        )
