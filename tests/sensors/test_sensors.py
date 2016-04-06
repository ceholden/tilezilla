import pytest
import six

from tilezilla import sensors


def test_friendly_names_data():
    # Test this variable is dict
    # Should contain [SENSOR (str)]:[MAPPING (dict)]
    # where:
    #   MAPPING is a dict of [friendly_name (str)]:[band id (int)]
    assert isinstance(sensors.SENSOR_FRIENDLY_NAMES, dict)
    sensor_names = ['TM', 'ETM+', 'MSS', 'OLI_TIRS']  # ...
    for name in sensor_names:
        assert name in sensors.SENSOR_FRIENDLY_NAMES

    for name, mapping in six.iteritems(sensors.SENSOR_FRIENDLY_NAMES):
        for band_name, band_idx in six.iteritems(mapping):
            assert isinstance(band_name, str)
            assert isinstance(band_idx, int)
