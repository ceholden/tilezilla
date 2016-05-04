""" Test for `tilezilla.core` classes
"""
import inspect

import rasterio
import pytest

import tilezilla.core as core


# Band -------------------------------------------------------------------------
@pytest.mark.parametrize('band_idx', [1, 2, 3])
def test_band(rgb_image, band_idx):
    band = core.Band(rgb_image, bidx=band_idx)

    with rasterio.open(rgb_image) as src:
        # Assert the properties are the same
        props = inspect.getmembers(src, lambda x: not callable(x))
        for prop, value in props:
            assert getattr(band.src, prop) == value

        filter_ = (lambda x: not callable(x) and
                             not isinstance(x, rasterio._io.RasterReader))
        props = inspect.getmembers(rasterio.band(src, band_idx), filter_)
        for prop, value in props:
            assert getattr(band.band, prop) == value
