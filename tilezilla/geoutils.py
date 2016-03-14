# -*- coding: utf-8 -*-
""" Utilities
"""
import logging
import os
from contextlib import contextmanager

import affine
from osgeo import osr
import rasterio
import shapely
import shapely.geometry
from rasterio import crs, warp

from .core import BoundingBox

logger = logging.getLogger('tilezilla')
osr.UseExceptions()


def match_to_grid(match, grid, pix_size):
    """ Return new postings for input that coalign with grid

    Args:
        match (iterable): X or Y coordinates of input extent to be repositioned
        grid_xy (iterable): X or Y coordinates of grid extent to match
        pix_size (iterable): X or Y pixel sizes of data to match

    Returns:
        tuple: new X/Y coordinate of matched input

    """
    new_coords = []

    for _grid, _match, ps in zip(grid, match, pix_size):
        offset = int(round((_grid - _match) / ps))
        new_coords.append(_grid - offset * ps)

    return new_coords


def snap_transform(transform, posting):
    """ Return a new :class:`Affine` with coordinates coaligned to a post

    Args:
        transform (affine.Affine): affine transform to snap
        posting (tuple): x/y pair of coordinates to snap the transform to

    Returns:
        affine.Affine: newly snapped Affine transform
    """
    ulx, uly = transform.c, transform.f
    gridx, gridy = posting
    snapx = gridx + round((ulx - gridx) / transform.a) * transform.a
    snapy = gridy + round((uly - gridy) / transform.e) * transform.e

    return affine.Affine(transform.a, transform.b, snapx,
                         transform.d, transform.e, snapy)


def intersects_bounds(a_bounds, b_bounds):
    """ Return True/False if a intersects b

    Args:
        a_bounds (iterable): bounds of a (left bottom right top)
        b_bounds (iterable): bounds of b (left bottom right top)

    Returns:
        bool: True/False if a intersects b

    """
    a = bounds_to_polygon(a_bounds)
    b = bounds_to_polygon(b_bounds)

    return a.intersects(b)


def bounds_to_polygon(bounds):
    """ Returns Shapely polygon of bounds

    Args:
        bounds (iterable): bounds (left bottom right top)

    Returns:
        shapely.geometry.Polygon: polygon of bounds

    """
    return shapely.geometry.Polygon([
        (bounds[0], bounds[1]),
        (bounds[2], bounds[1]),
        (bounds[2], bounds[3]),
        (bounds[0], bounds[3])
    ])


def meta_to_bounds(affine, width, height, **kwargs):
    """ Convert ``rasterio`` **dataset.meta to a BoundingBox

    Args:
        affine (affine.Affine): Affine transformation
        width (int): Number of columns
        height (int): Number of rows

    Returns:
        BoundingBox: The box bounding the extent of the raster
    """
    a, b, c, d, e, f, _, _, _ = affine
    return BoundingBox(c, f + e * height, c + a * width, f)


def reproject_bounds(bounds, src_crs, dst_crs):
    """ Return bounds reprojected to `dst_crs`

    Args:
        BoundingBox: Bounding box in `src_crs`
        src_crs (str or dict): The coordinate reference system, interpretable
            by rasterio
        dst_crs (str or dict): The coordinate reference system, interpretable
            by rasterio

    Returns:
        BoundingBox: Bounding box in `dst_crs`

    """
    if not crs.is_same_crs(src_crs, dst_crs):
        return BoundingBox(*warp.transform_bounds(src_crs, dst_crs, *bounds))
    else:
        return bounds


def crs_to_wkt(src_crs):
    """ Return WKT representation of a rasterio dataset's CRS

    Args:
        src_crs (`dict`): Rasterio dataset CRS

    Returns:
        str: WKT of CRS
    """
    sr = osr.SpatialReference()
    sr.ImportFromProj4(crs.to_string(src_crs))

    return sr.ExportToWkt()


@contextmanager
def reproject_as_needed(src, tilespec, resampling='nearest'):
    """ Return a ``rasterio`` dataset, reprojected if needed

    Returns src dataset if reprojection unncessary. Otherwise returns an in
    memory ``rasterio`` dataset. Reprojection will snap the bounding
    coordinates of the source dataset to align with the tile specification.

    Args:
        src (rasterio._io.RasterReader): rasterio raster dataset
        tilespec (TileSpec): tile specification
        resampling (str): reprojection resampling method (default: nearest)

    Returns:
        rasterio._io.RasterReader: original or reprojected dataset
    """
    if crs.is_same_crs(src.crs, tilespec.crs):
        yield src
    else:
        # Calculate new affine & size
        affine, width, height = warp.calculate_default_transform(
            src.crs, tilespec.crs,
            src.width, src.height,
            *src.bounds, resolution=tilespec.res)
        # Snap bounds
        affine = snap_transform(affine, tilespec.ul)

        dst_meta = src.meta.copy()
        dst_meta['driver'] = 'MEM'
        dst_meta['crs'] = tilespec.crs
        dst_meta['width'] = width
        dst_meta['height'] = height
        dst_meta['affine'] = affine
        dst_meta['transform'] = affine

        with rasterio.open(os.path.basename(src.name), 'w', **dst_meta) as dst:
            warp.reproject(
                rasterio.band(src, 1),
                rasterio.band(dst, 1),
                resampling=getattr(warp.RESAMPLING, resampling)
            )
            yield dst
