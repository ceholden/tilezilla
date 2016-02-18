import os
import tarfile

import pytest


@pytest.fixture(scope='module')
def ESPA_archive(request):
    """ ESPA download archive filename
    """
    return os.path.join(os.path.dirname(__file__), 'data',
                        'LT50120312002300-SC20151009172149.tar.gz')


@pytest.fixture(scope='module')
def ESPA_archive_EPSG5070(request):
    """ ESPA download archive filename, reprojected to EPSG:5070
    """
    return os.path.join(os.path.dirname(__file__), 'data',
                        'LT50120312002300-SC20151009172149_EPSG5070.tar.gz')


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
