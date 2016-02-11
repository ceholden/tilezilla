""" Helper functions/etc for use within this package
"""
from functools import reduce, wraps


def lazy_property(prop):
    """ Lazily populate and return a class property (i.e., memoize)

    A quick way of reusing the memoize idiom for your class properties
    """
    prop_name = '_{}'.format(prop.__name__)

    @wraps(prop)
    def wrapper(self):
        if not hasattr(self, prop_name):
            setattr(self, prop_name, prop(self))
        return getattr(self, prop_name)

    return property(wrapper)


def dict_keymap_get(d, keys):
    """ Get value from a list of keys for a nested dictionary

    Source: http://stackoverflow.com/a/14692747
    """
    return reduce(lambda _d, _k: _d[_k], keys, d)


def dict_keymap_set(d, keys, key, value):
    """ Set value from a list of keys for a nested dictionary

    Source: http://stackoverflow.com/a/14692747
    """
    dict_keymap_get(d, keys[:-1])[keys[-1]][key] = value
