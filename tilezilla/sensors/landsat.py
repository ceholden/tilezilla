""" Module for dealing with Landsat sensors
"""
from collections import OrderedDict
import re

import arrow
from bs4 import BeautifulSoup
import numpy as np
import pathlib
import six

from . import SENSOR_FRIENDLY_NAMES
from .._util import lazy_property
from ..core import Band, BoundingBox


#: dict[sensor=dict[friedly_name=band number]]
sensor_bands_friendly_name = {
    'LM': SENSOR_FRIENDLY_NAMES['MSS'],
    'LT': SENSOR_FRIENDLY_NAMES['TM'],
    'LE': SENSOR_FRIENDLY_NAMES['ETM+'],
    'LC': SENSOR_FRIENDLY_NAMES['OLI_TIRS']
}


def description_to_friendly_name(sensor, desc):
    """ Return friendly name of band given description and sensor

    Args:
        sensor (str): Landsat sensor [LM, LT, LE, LC]
    """
    if sensor not in sensor_bands_friendly_name:
        return ''
    switch = sensor_bands_friendly_name[sensor]
    for k, v in six.iteritems(switch):
        if re.match('.*{}($|[^0-9].*)'.format(v), desc):
            return k


def parse_MTL(fid):
    """ Return an ordered dict from a Landsat "MTL" metadata file

    Args:
        fid (file descriptor): file descriptor for "MTL" metadata file

    Returns:
        OrderedDict: dict of MTL file
    """
    data = OrderedDict()
    for line in fid:
        split = str(line).split(' = ')
        if len(split) == 2:
            data[split[0].strip().strip('"')] = split[1].strip().strip('"')
    return data


class MTL(object):
    """ Landsat "MTL" metadata file

    Args:
        path (str): Path to the metadata file
        data (OrderedDict): metadata contained within the MTL file
    """
    def __init__(self, path, data):
        self.path = pathlib.Path(str(path)).resolve()
        self.data = data

    @lazy_property
    def scene_id(self):
        """ Landsat scene ID (e.g., LT50120312002300LGS01)
        """
        return self.data['LANDSAT_SCENE_ID']

    @lazy_property
    def LPGS(self):
        """ Level-1 Product Generation System version number
        """
        return self.data['PROCESSING_SOFTWARE_VERSION']

    @lazy_property
    def product_level(self):
        """ Level-1 product level (L1G, L1T, etc.)
        """
        return self.data['DATA_TYPE']

    @lazy_property
    def sensor(self):
        """ Landsat sensor (e.g., LT4, LT5)
        """
        return self.data['SPACECRAFT_ID']

    @lazy_property
    def path_row(self):
        """ WRS-2 path and row
        """
        path = self.data['WRS_PATH']
        row = self.data['WRS_ROW']
        return path, row

    @lazy_property
    def cloud_cover(self):
        """ ACCA cloud cover score
        """
        return float(self.data['CLOUD_COVER'])

    @classmethod
    def from_file(cls, path):
        """
        Args:
            path (str): path to the MTL file

        Returns:
            MTL: Instance of MTL
        """
        with open(path, 'r') as fid:
            return cls(path, parse_MTL(fid))

    @classmethod
    def from_fid(cls, fid):
        """
        Args:
            fid (file descriptor): file descriptor for "MTL" metadata file

        Returns:
            MTL: Instance of MTL
        """
        from IPython.core.debugger import Pdb; Pdb().set_trace()
        return cls(parse_MTL(fid))


class ESPAMetadata(object):
    """ ESPA Metadata parsing

    Args:
        path (str): Path to metadata file
        data (BeautifulSoup): A BeautifulSoup of the XML metadata
    """
    def __init__(self, path, data):
        self.path = pathlib.Path(str(path)).resolve()
        self.data = data

    @classmethod
    def from_file(cls, path):
        return cls(path, BeautifulSoup(open(str(path)), 'lxml'))

    @property
    def instrument(self):
        """ str: instrument taking acquisition measurement
        """
        return self.data.find('instrument').text

    @property
    def platform(self):
        """ str: platform holding instrument for this acquisition
        """
        return self.data.find('satellite').text

    @property
    def acquired(self):
        """ Arrow: date and time of acquisition

        The time of this acquisition is taken as the scene center time.
        """
        ad = self.data.find('acquisition_date').text
        ct = self.data.find('scene_center_time').text
        return arrow.get('{}T{}'.format(ad, ct))

    @property
    def processed(self):
        """ Arrow: date and time of processing
        """
        return arrow.get(self.data.find('production_date').text)

    @property
    def solar_azimuth(self):
        """ float: solar azimuth angle during acqusition
        """
        return float(self.data.find('solar_angles').attrs['azimuth'])

    @property
    def solar_zenith(self):
        """ float: solar zenith angle during acquisition
        """
        return float(self.data.find('solar_angles').attrs['zenith'])

    @property
    def bounds(self):
        _xml = self.data.find('bounding_coordinates')
        return BoundingBox(
            left=float(_xml.find('west').text),
            top=float(_xml.find('north').text),
            bottom=float(_xml.find('south').text),
            right=float(_xml.find('east').text)
        )

    @lazy_property
    def bands(self):
        bands = []
        for _xml in self.data.find_all('band'):
            bands.append(self._xml_to_band(_xml))
        return bands

    def _xml_to_band(self, xml):
        """ Parse a bit of XML to a Band
        """
        def str2dtype(s, dtype):
            if not s:
                return None
            if dtype.kind in ('u', 'i'):
                return int(s)
            else:
                return float(s)
        # Names
        standard_name = xml.get('name')
        short_name = xml.find('short_name').text
        long_name = xml.find('long_name').text
        friendly_name = (description_to_friendly_name(short_name[0:2],
                                                      standard_name)
                         or standard_name)

        # Units
        units = xml.find('data_units').text
        # Filename path
        path = str(self.path.parent.joinpath(xml.find('file_name').text))
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
                    friendly_name=friendly_name,
                    units=units, fill=fill,
                    valid_min=_min, valid_max=_max, scale_factor=scale_factor)
