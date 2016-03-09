""" User supplied configuration settings
"""
import logging
import os
import pkgutil

import jsonschema
import six
import yaml

from .errors import ConfigException
from .tilespec import TileSpec, TILESPECS

logger = logging.getLogger('tilezilla')


# TODO: load schema & validate
def parse_config(path):
    """ Parse a configuration file and return it as a dict

    Args:
        path (str): Location of YAML configuration file

    Returns:
        dict: Configuration options

    Raises:
        KeyError: Raise if configuration file is missing required sections or
            is otherwise malformed
    """
    with open(path) as f:
        cfg = yaml.safe_load(f)

    # Validate
    schema = pkgutil.get_data('tilezilla', 'data/config_schema.yaml')
    schema_defn = yaml.load(schema)

    jsonschema.validate(cfg, schema_defn)

    # Final parsing
    cfg = _parse_database(cfg)
    cfg = _parse_tilespec(cfg)

    return cfg


# SECTIONS
def _parse_database(cfg):
    # Ensure writeable
    root = os.path.dirname(cfg['database']['database'])
    if not os.access(root, os.W_OK) or not os.path.exists(root):
        raise ConfigException(
            'Database file ("database" in config) root directory '
            'does not exist: {}'.format(root))
    return cfg


def _parse_tilespec(cfg):
    _tilespec = cfg['tilespec']
    if isinstance(_tilespec, str):
        if _tilespec not in TILESPECS:
            raise KeyError('Unknown tile specification "{}"'
                           .format(_tilespec))
        cfg['tilespec'] = TILESPECS[_tilespec]
    elif isinstance(_tilespec, dict):
        cfg['tilespec'] = TileSpec(**cfg['tilespec'])

    return cfg


# UTIL
def _expand_envvars(d):
    """ Recursively convert lookup that look like environment vars in a dict

    This function things that environmental variables are values that begin
    with `$` and are evaluated with :func:`os.path.expandvars`. No exception
    will be raised if an environment variable is not set.

    Taken from YATSM library:
    https://github.com/ceholden/yatsm/blob/master/yatsm/config_parser.py

    Args:
        d (dict): Expand environment variables used in the values of this
            dictionary

    Returns:
        dict: Input dictionary with environment variables expanded
    """
    def check_envvar(k, v):
        """ Warn if value looks un-expanded """
        if '$' in v:
            logger.warning('Config key=value pair might still contain '
                           'environment variables: "%s=%s"' % (k, v))

    _d = d.copy()
    for k, v in six.iteritems(_d):
        if isinstance(v, dict):
            _d[k] = _expand_envvars(v)
        elif isinstance(v, str):
            _d[k] = os.path.expandvars(v)
            check_envvar(k, v)
        elif isinstance(v, (list, tuple)):
            n_v = []
            for _v in v:
                if isinstance(_v, str):
                    _v = os.path.expandvars(_v)
                    check_envvar(k, _v)
                n_v.append(_v)
            _d[k] = n_v
    return _d
