""" Handler for Landsat data processed and distributed through ESPA
"""
from .._util import find_in_path
from ..sensors.landsat import MTL, ESPAMetadata
from .core import BaseProduct


class ESPALandsat(BaseProduct):
    """ ESPA processed "Level 2" Landsat data
    """
    xml_pattern = 'L*.xml'
    mtl_pattern = 'L*_MTL.txt'

    description = 'ESPALandsat'

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
        # if not mtl_file:
        #     raise IOError('Cannot find MTL metadata file in {}'.format(path))
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
                          'pattern ({}): {}'.format(cls.xml_pattern, xml_file))

        md_files = dict(MTL=str(mtl_file[0]) if mtl_file else None,
                        ESPAMetadata=str(xml_file[0]))
        mtl = MTL.from_file(md_files['MTL']) if md_files['MTL'] else None
        xml = ESPAMetadata.from_file(md_files['ESPAMetadata'])

        return cls(
            timeseries_id=xml.scene_id,
            acquired=xml.acquired, processed=xml.processed,
            platform=xml.platform, instrument=xml.instrument,
            bounds=xml.bounds,
            bands=list(xml.bands), metadata=mtl.data if mtl else {},
            metadata_files=md_files
        )
