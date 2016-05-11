""" Tests for tilezilla.products.espa
"""
import fnmatch
import os

from tilezilla.products import espa

from . import check_attributes

# ESPA GeoTIFF order ----------------------------------------------------------
def test_ESPA_geotiff(ESPA_GTiff_order):
    product = espa.ESPALandsat.from_path(ESPA_GTiff_order)
    check_attributes(product)


def test_ESPA_geotiff_noMTL(ESPA_GTiff_order):
    """ Ensure ESPALandsat can read product w/o MTL file
    """
    mtl = fnmatch.filter(os.listdir(ESPA_GTiff_order), 'L*MTL.txt')
    os.remove(os.path.join(ESPA_GTiff_order, mtl[0]))

    product = espa.ESPALandsat.from_path(ESPA_GTiff_order)
    check_attributes(product)
    assert product.metadata == {}
