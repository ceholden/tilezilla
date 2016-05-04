import os
import tarfile

import pytest

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')


@pytest.fixture
def rgb_image(request):
    return os.path.join(DATA, 'red_nir_swir1.gtif')


@pytest.fixture(scope='module')
def ESPA_archive(request):
    """ ESPA download archive filename
    """
    return os.path.join(DATA, 'LT50120312002300-SC20151009172149.tar.gz')


@pytest.fixture(scope='module')
def ESPA_archive_EPSG5070(request):
    """ ESPA download archive filename, reprojected to EPSG:5070
    """
    return os.path.join(DATA, 'LT50120312002300-SC20151009172149_EPSG5070.tar.gz')


@pytest.fixture(scope='module')
def ESPA_order(request, ESPA_archive, tmpdir_factory):
    """ Extract ``ESPA_archive`` to temporary directory
    """
    path = str(tmpdir_factory.mktemp('ESPA_order'))
    with tarfile.open(ESPA_archive) as tgz:
        tgz.extractall(path)
    return path


@pytest.fixture(scope='module')
def ESPA_order_EPSG5070(request, ESPA_archive_EPSG5070, tmpdir_factory):
    """ Extract ``ESPA_archive_EPSG5070`` to temporary directory
    """
    path = str(tmpdir_factory.mktemp('ESPA_order_EPSG5070'))
    with tarfile.open(ESPA_archive_EPSG5070) as tgz:
        tgz.extractall(path)
    return path
