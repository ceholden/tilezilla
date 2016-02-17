""" Helper functions/etc for use within this package
"""
import shutil
import tarfile
import tempfile
from contextlib import contextmanager
from functools import wraps


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


@contextmanager
def decompress_to(archive):
    """ Extract archive to temporary directory and yield path

    Args:
        archive (str): tar, tar.gz, etc. file

    Yields:
        str: path to directory containing extracted archive
    """
    try:
        _tmp = tempfile.mkdtemp()
        with tarfile.open(archive) as tgz:
            tgz.extractall(_tmp)
        yield _tmp
    finally:
        shutil.rmtree(_tmp)
