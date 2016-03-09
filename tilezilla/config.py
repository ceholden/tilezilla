""" User supplied configuration settings
"""
import logging
import os

import six

logger = logging.getLogger('tilezilla')


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
