""" Handler for Landsat data processed and distributed through ESPA
"""
import glob
import os
import pprint
import textwrap

import arrow
from bs4 import BeautifulSoup
import numpy as np

from .core import BaseProduct
from .._util import lazy_property
from ..core import Band, BoundingBox
from ..sensors.landsat import MTL


class ESPALandsat(BaseProduct):
    """ ESPA processed "Level 2" Landsat data

    Args:
        path (str): the path to the root directory of the extracted data
            product

    Raises:
        IOError: raise if MTL or ESPA product metadata cannot be found
    """
    def __init__(self, path, xml_pattern='L*.xml', mtl_pattern='L*_MTL.txt'):
        self.path = path
        self.xml_pattern = xml_pattern
        self.mtl_pattern = mtl_pattern

        self.mtl_file = glob.glob(os.path.join(self.path, self.mtl_pattern))
        if not self.mtl_file:
            raise IOError('Cannot find MTL metadata file in {}'
                          .format(self.path))
        if len(self.mtl_file) > 1:
            raise IOError('Found multiple files matching MTL file search '
                          'pattern ({}): {}'
                          .format(self.mtl_pattern, self.mtl_file))

        self.xml_file = glob.glob(os.path.join(self.path, self.xml_pattern))
        if not self.xml_file:
            raise IOError('Cannot find ESPA XML metadata file in {}'
                          .format(self.path))
        if len(self.xml_file) > 1:
            raise IOError('Found multiple files matching ESPA XML file search '
                          'pattern ({}): {}'
                          .format(self.xml_pattern, self.xml_file))

        self.mtl_file = os.path.abspath(self.mtl_file[0])
        self.xml_file = os.path.abspath(self.xml_file[0])

        #: MTL: Landsat "MTL" metadata file
        self.mtl = MTL(self.mtl_file)
        #: BeautifulSoup: Landsat ESPA order XML metadata file
        self.xml = BeautifulSoup(open(self.xml_file), 'lxml')

    def __repr__(self):
        s = """
        EROS Science Processing Architecture (ESPA) Landsat product

        Scene ID: {scene_id}
        Acquisition date time: {time}
        Bounding Box:
            Top:        {uly}
            Left:       {ulx}
            Bottom:     {lry}
            Right:      {lrx}

        Bands: {nbands}
        {band_names}
        """.format(
            scene_id=self.timeseries_id,
            time=self.time,
            uly=self.bounding_box.top,
            ulx=self.bounding_box.left,
            lry=self.bounding_box.bottom,
            lrx=self.bounding_box.right,
            nbands=len(self.bands),
            band_names='\n'.join(
                [''] + [' ' * 12 + b.long_name for b in self.bands])
        )
        return textwrap.dedent(s)

    @lazy_property
    def bounding_box(self):
        """ BoundingBox: bounding box of product in latitude, longitude
        """
        _xml = self.xml.find('bounding_coordinates')
        return BoundingBox(
            left=float(_xml.find('west').text),
            top=float(_xml.find('north').text),
            bottom=float(_xml.find('south').text),
            right=float(_xml.find('east').text)
        )

    @lazy_property
    def bands(self):
        """ list[:class:`Band`]: bands contained within ESPA dataset
        """
        bands = []
        for _xml in self.xml.find_all('band'):
            bands.append(self._xml_to_band(_xml))
        return bands

    @property
    def timeseries_id(self):
        """ str: the Landsat acquistion scene ID
        """
        return self.mtl.scene_id

    @lazy_property
    def time(self):
        """ Arrow: date and time of acquisition

        The time of this acquisition is taken as the scene center time.
        """
        ad = self.xml.find('acquisition_date').text
        ct = self.xml.find('scene_center_time').text
        return arrow.get('{}T{}'.format(ad, ct))

    @lazy_property
    def instrument(self):
        """ str: instrument taking acquisition measurement
        """
        return self.xml.find('instrument').text

    @lazy_property
    def platform(self):
        """ str: platform holding instrument for this acquisition
        """
        return self.xml.find('satellite').text

    @property
    def metadata_files(self):
        """ dict: name and paths to metadata files for this observation
        """
        return dict(MTL=self.mtl_file, ESPA_XML=self.xml_file)

    @lazy_property
    def solar_azimuth(self):
        """ float: solar azimuth angle during acqusition
        """
        return self.xml.find('solar_angles').azimuth

    @lazy_property
    def solar_zenith(self):
        """ float: solar zenith angle during acquisition
        """
        return self.xml.find('solar_angles').zenith

    def _xml_to_band(self, xml):
        """ Parse a bit of XML to a Band """
        def str2dtype(s, dtype):
            if not s:
                return None
            if dtype.kind in ('u', 'i'):
                return int(s)
            else:
                return float(s)
        # Names
        standard_name = xml.get('name')
        long_name = xml.find('long_name').text
        units = xml.find('data_units').text
        # Filename path
        path = os.path.join(self.path,
                            xml.find('file_name').text)
        # Numeric info
        data_type = np.dtype(xml.get('data_type').lower())

        fill = str2dtype(xml.get('fill_value'), data_type)
        valid_range = xml.find('valid_range')
        _min = str2dtype(valid_range.get('min'), data_type)
        _max = str2dtype(valid_range.get('max'), data_type)
        scale_factor = xml.get('scale_factor')
        if scale_factor:
            scale_factor = float(scale_factor)

        return Band(path, 1,
                    standard_name=standard_name, long_name=long_name,
                    units=units, fill=fill,
                    valid_min=_min, valid_max=_max, scale_factor=scale_factor)
