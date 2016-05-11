import os
import tarfile

import pytest

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')


@pytest.fixture
def rgb_image(request):
    return os.path.join(DATA, 'red_nir_swir1.gtif')


# ESPA --  data  --------------------------------------------------------
@pytest.fixture(params=[
    'LE70130301999195-SC20151019134154.tar.gz',
    'LE70130312015175-SC20151019173810.tar.gz',
    'LT40130301987146-SC20151019150137.tar.gz',
    'LT50120312002300-SC20151009172149.tar.gz',
    'LT50130301994205-SC20151019145346.tar.gz',
])
def ESPA_GTiff_archive(request):
    """ ESPA  GeoTIFF data download archive filename
    """
    return os.path.join(DATA, request.param)


@pytest.fixture
def ESPA_GTiff_order(ESPA_GTiff_archive,
                     request, tmpdir_factory):
    """ ESPA_GTiff_archive extracted to temporary directory
    """
    path = str(tmpdir_factory.mktemp('ESPA_order'))
    with tarfile.open(ESPA_GTiff_archive) as tgz:
        tgz.extractall(path)
        path = os.path.join(path, os.path.commonpath(tgz.getnames()))
    return path


@pytest.fixture(params=['LT50120312002300-SC20151009172149_EPSG5070.tar.gz'])
def ESPA_GTiff_archive_EPSG5070(request):
    """ ESPA  GeoTIFF data download archive filename in EPSG:5070
    """
    return os.path.join(DATA, request.param)


@pytest.fixture
def ESPA_GTiff_order_EPSG5070(ESPA_GTiff_archive_EPSG5070,
                              request, tmpdir_factory):
    """ ESPA_GTiff_archive_EPSG5070 extracted to temporary directory
    """
    path = str(tmpdir_factory.mktemp('ESPA_order_EPSG5070'))
    with tarfile.open(ESPA_GTiff_archive_EPSG5070) as tgz:
        tgz.extractall(path)
        path = os.path.join(path, os.path.commonpath(tgz.getnames()))
    return path
