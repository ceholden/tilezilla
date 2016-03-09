import os

from tilezilla import config_parser


# ENVIRONMENT VARIABLE PARSING
def test_get_envvars():
    """ Taken from YATSM project:
    https://github.com/ceholden/yatsm/blob/master/tests/test_config_parser.py
    """
    truth = {
        'database': {
            'driver': 'sqlite',
            'uri': '/tmp/tiles/tilezilla.db'
        }
    }
    d = {
        'database': {
            'driver': '$TILEZILLA_DRIVER',
            'uri': '$TILEZILLA_ROOTDIR/tiles/tilezilla.db'
        }
    }
    envvars = {
        'TILEZILLA_DRIVER': 'sqlite',
        'TILEZILLA_ROOTDIR': '/tmp'
    }
    # Backup and replace environment
    backup = os.environ.copy()
    for k in envvars:
        os.environ[k] = envvars[k]

    expanded = config_parser.expand_envvars(d)
    os.environ.update(backup)

    assert truth == expanded
