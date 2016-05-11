""" Tests for yatsm._util
"""
import os

from mock import Mock
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
def test_decompress_to(ESPA_GTiff_order, ESPA_GTiff_archive):
    espa_files = []
    for root, dirs, files in os.walk(ESPA_GTiff_order):
        espa_files.extend(files)

    with _util.decompress_to(ESPA_GTiff_archive) as path:
        tgz_files = []
        for root, dirs, files in os.walk(path):
            tgz_files.extend(files)

    assert all([f in espa_files for f in tgz_files])
    assert not os.path.exists(path)  # path should be deleted when context ends


def test_decompress_to_notarchive(ESPA_GTiff_order):
    with _util.decompress_to(ESPA_GTiff_order) as path:
        assert path == ESPA_GTiff_order


# mkdir_p
def test_mkdir_p_success(tmpdir):
    _util.mkdir_p(tmpdir.join('test').strpath)


def test_mkdir_p_succcess_exists(tmpdir):
    _util.mkdir_p(tmpdir.join('test').strpath)
    _util.mkdir_p(tmpdir.join('test').strpath)


def test_mkdir_p_failure_permission(tmpdir):
    with pytest.raises(OSError):
        _util.mkdir_p('/asdf')


# find_in_path
@pytest.fixture
def ex_tmpdir(tmpdir):
    d1, d2 = tmpdir.mkdir('dir1'), tmpdir.mkdir('dir2')
    d1.join('Landsat_MTL.txt').ensure()
    d1.join('Landsat_MTL.txt.gz').ensure()
    d2.join('not_found.txt').ensure()
    return tmpdir


def test_find_in_path_success_1(ex_tmpdir):
    assert len(_util.find_in_path(str(ex_tmpdir), 'L*MTL.txt')) == 1
    assert len(_util.find_in_path(str(ex_tmpdir), '*.txt')) == 2


def test_find_in_path_success_2(ex_tmpdir):
    assert len(_util.find_in_path(str(ex_tmpdir), '^L.*.MTL.txt$', True)) == 1
    assert len(_util.find_in_path(str(ex_tmpdir), '.*.txt$', True)) == 2


def test_find_in_path_success_3(ex_tmpdir):
    assert len(_util.find_in_path(str(ex_tmpdir), '^asdf$', True)) == 0
    assert len(_util.find_in_path(str(ex_tmpdir), '^asdf$')) == 0


# multiple_filter
@pytest.fixture
def ex_strings(request):
    return [
    'Landsat_sr_band1.tif',
    'Landsat_cfmask.tif',
    'METADATA',
    'SOMETHING.xml',
    'Landsat_temp.tif'
]


def test_multiple_filter_success_1(ex_strings):
    patterns = ['L*sr_band*.tif', '*.xml']
    matched = _util.multiple_filter(ex_strings, patterns, False)
    assert sorted(matched) == matched
    assert matched == ['Landsat_sr_band1.tif', 'SOMETHING.xml']


def test_multiple_filter_success_2(ex_strings):
    pattern = '^L.*sr_band.*.tif$'
    matched = _util.multiple_filter(ex_strings, pattern, regex=True)
    assert len(matched) == 1
    assert matched == ['Landsat_sr_band1.tif']


# include_bands
@pytest.mark.parametrize(
    ('include', 'regex', 'answer'), [
    ({'long_name': ['*surface reflectance*']}, False, ['blue', 'red']),
    ({'long_name': ['*surface reflectance*', '*bright*']}, False, ['blue', 'red', 'temp']),
    ({'friendly_name': ['blue', 'red']}, False, ['blue', 'red']),
    ({'long_name': ['.*surface reflectance.*']}, True, ['blue', 'red'])
])
def test_include_bands_1(include, regex, answer):
    bands = []

    friendly_names = ['blue', 'red', 'temp']
    long_names = [
        'band 1 surface reflectance',
        'band 2 surface reflectance',
        'toa brightness temperature'
    ]
    for friendly_name, long_name in zip(friendly_names, long_names):
        bands.append(Mock(long_name=long_name, friendly_name=friendly_name))

    included_bands = _util.include_bands(bands, include, regex=regex)
    assert answer == [b.friendly_name for b in included_bands]
