""" Helper functions/etc for use within this package
"""
from collections import OrderedDict
import errno
import fnmatch
import os
import pathlib
import re
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
def decompress_to(archive_or_directory):
    """ Extract archive to temporary directory, if necessary, and yield path

    Args:
        archive_or_directory (str): Path to a directory or archive (tar,
            tar.gz, etc. file)

    Yields:
        str: path to directory containing extracted archive
    """
    try:
        if os.path.isdir(archive_or_directory):
            _tmp = None
            yield archive_or_directory
        else:
            _tmp = tempfile.mkdtemp(prefix='tilezilla_')
            with tarfile.open(archive_or_directory) as tgz:
                tgz.extractall(_tmp)
                yield _tmp
    finally:
        if _tmp:
            shutil.rmtree(_tmp)


def mkdir_p(d):
    """ Make a directory, ignoring error if it exists (i.e., ``mkdir -p``)
    Args:
        d (str): directory path to create
    Raises:
        OSError: Raise OSError if cannot create directory for reasons other
            than it existing already (errno 13 "EEXIST")
    """
    try:
        os.makedirs(d)
    except OSError as err:
        # File exists
        if err.errno == errno.EEXIST:
            pass
        else:
            raise err


def find_in_path(path, patterns, regex=False):
    """ Return a sequence of paths that match a given pattern in a directory

    Args:
        path (str): The root folder to find within
        patterns (tuple[str]): Search patterns, either glob style or a regular
            expression
        regex (bool): True if ``pattern`` is glob style, else False

    Returns:
        list[pathlib.Path]:
    """
    found = []
    for root, dirs, files in os.walk(str(path)):
        matched = multiple_filter(sorted(files), patterns, regex=regex)
        found.extend([pathlib.Path(root).joinpath(fname).resolve()
                      for fname in matched])
    return found


def multiple_filter(strings, patterns, regex=False):
    """ Apply multiple search filters to a sequence of strings

    Args:
        strings (list[str]): A collection of strings to search
        patterns (list[str]): A collection of search patterns, etiher glob
            style or regular expression
        regex (bool): True if ``patterns`` is a set of regular expressions

    Returns:
        list[str]: A subset of ``strings`` that matched a pattern in
            ``patterns``
    """
    if isinstance(patterns, str):
        patterns = (patterns, )
    if not regex:
        patterns = map(fnmatch.translate, patterns)
    regexs = map(re.compile, patterns)

    found = []
    for _regex in regexs:
        for s in strings:
            if _regex.search(s):
                found.append(s)
    uniq_found = sorted(set(found), key=lambda item: found.index(item))
    return uniq_found


def include_bands(bands, include, regex=False):
    """ Include subset of ``bands`` based on ``include``

    Args:
        bands (list[Band]): Bands to filter
        include (dict): Dictionary of 'attribute':['pattern',] used to filter
            input bands for inclusion
        regex (bool): True if patterns in ``include`` are sets of regular
            expressions

    Returns:
        list[Band]: Included bands
    """
    out = []
    for attr in include:
        attrs = OrderedDict(((getattr(b, attr), b) for b in bands))
        match = multiple_filter(attrs.keys(), include[attr], regex=regex)
        out.extend([attrs[k] for k in match])
    return sorted(set(out), key=lambda item: out.index(item))
