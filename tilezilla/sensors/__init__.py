""" Sensor specific information or helper functions/classes
"""
import json
import pkgutil


# Load sensor friendly names from pkgdata
def retrieve_friendly_names():
    """ Retrieve sensor 'friendly names'

    Returns:
        dict:
    """
    data = pkgutil.get_data('tilezilla', 'data/friendly_names.json').decode()
    return json.loads(data)


SENSOR_FRIENDLY_NAMES = retrieve_friendly_names()
