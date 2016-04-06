""" Sensor specific information or helper functions/classes
"""
import json
import os
import pkgutil


_SENSOR_FRIENDLY_NAMES_DATA = os.path.join('data', 'friendly_names.json')

SENSOR_FRIENDLY_NAMES = json.loads(
    pkgutil.get_data('tilezilla', _SENSOR_FRIENDLY_NAMES_DATA).decode()
)
