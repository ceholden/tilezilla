""" Tests for yatsm._util
"""
import os

import pytest

from tilezilla import _util


# lazy_property
@pytest.fixture
def test_object():
    class TestObject(object):
        def __init__(self, b):
            self.b = b

        @_util.lazy_property
        def a(self):
            return {'a': 5}

    return TestObject(10)


def test_lazy_property_1(test_object):
    # Should have attr 'b' from __init__
    assert hasattr(test_object, 'b')
    # Should not have 'a' in dict
    assert 'a' not in test_object.__dict__
    # Should not have 'hidden' attr before access
    assert not hasattr(test_object, '_a')


def test_lazy_property_2(test_object):
    # If we try to access 'a', then it should have it
    assert hasattr(test_object, 'a')
    # In fact, it should be a reference the same, 'hidden' object!
    assert test_object.a is test_object._a


# decompress_to
def test_decompress_to(ESPA_order, ESPA_archive):
    espa_files = []
    for root, dirs, files in os.walk(ESPA_order):
        espa_files.extend(files)

    with _util.decompress_to(ESPA_archive) as path:
        tgz_files = []
        for root, dirs, files in os.walk(path):
            tgz_files.extend(files)

    assert all([f in espa_files for f in tgz_files])
    assert not os.path.exists(path)  # path should be deleted when context ends
