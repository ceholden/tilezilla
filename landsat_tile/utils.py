# -*- coding: utf-8 -*-
""" Utilities
"""
import itertools
import logging
from math import ceil
import os

import numpy as np
import rasterio.coords
import rasterio.crs
import rasterio.warp
import shapely
import shapely.geometry

logger = logging.getLogger('landsat_tile')


def calc_tile_intersection(bounds, crs):
    u""" Calculate bounds intersection with 1x1° tiles

      Args:
        bounds (BoundingBox): bounding box (left, botttom, right, top)
        crs (dict): coordinate reference system dict readable by rasterio

      Returns:
        tuple: tuple of ((lon, lat), ...) upper left corners intersecting
            provided bounds

    """
    # Get back as coordinates for UL, UR, LR, LL
    lons, lats = rasterio.warp.transform(
        crs, {'init': 'epsg:4326'},
        (bounds[0], bounds[2], bounds[2], bounds[0]),
        (bounds[3], bounds[3], bounds[1], bounds[1]))

    # Left is always floor for longitudes
    lons = np.floor(lons)
    # Upper is always ceil of latitudes
    lats = np.ceil(lats)

    lons = np.arange(min(lons), max(lons) + 1)
    lats = np.arange(min(lats), max(lats) + 1)

    # All possible combinations
    return tuple(itertools.product(lons, lats))


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


def tile_grid_parameters(lon, lat, grid):
    """ Return bounds, affine transform, and size of lon/lat tile in grid crs

    Args:
      lon (float): longitude
      lat (float): latitude
      grid (dict): grid parameters, including 'bounds', 'res', and 'crs'

    Returns:
      dict: bounds, affine transform, width, height, bounds_lonlat

    """
    # Formulate tile bounds
    bounds_lonlat = rasterio.coords.BoundingBox(
        left=lon, bottom=lat - 1, right=lon + 1, top=lat)

    # Reproject tile bounds to grid CRS
    xs, ys = rasterio.warp.transform(
        {'init': 'epsg:4326'}, grid['crs'],
        [lon, lon, lon + 1, lon + 1],
        [lat, lat - 1, lat, lat - 1])
    bounds_crs = rasterio.coords.BoundingBox(
        left=min(xs), bottom=min(ys), right=max(xs), top=max(ys))

    # Co-register reprojected tile bounds to grid
    xmin, ymin, xmax, ymax = rasterio.coords.BoundingBox(
        *match_to_grid(bounds_crs, grid['bounds'], grid['res'] * 2))
    logger.debug('Tile coordinates: {bbox}'.format(
        bbox=rasterio.coords.BoundingBox(xmin, ymin, xmax, ymax)))

    out = {}
    out['bounds_lonlat'] = bounds_lonlat
    out['bounds'] = rasterio.coords.BoundingBox(xmin, ymin, xmax, ymax)
    out['transform'] = rasterio.Affine(grid['res'][0], 0, xmin,
                                       0, -grid['res'][1], ymax)
    out['width'] = max(int(ceil((xmax - xmin) / grid['res'][0])), 1)
    out['height'] = max(int(ceil((ymax - ymin) / grid['res'][1])), 1)

    return out


def get_tile_output_name(source, tile_dir, lon, lat, ext=None, decimals=0):
    """ Return destination filename for a tile

    Filename will be:
        ${tile_dir}/$(format $lat)_$(format lon)/\
            $(basename $(dirname $source))/$(basename $source).${ext}

    Args:
      source (str): path to source filename
      tile_dir (str): path to tile root directory
      lon (float): longitude of upper left of tile
      lat (float): latitude of upper left of tile
      ext (str): file format extension (default: None)
      decimals (int): number of decimal places to retain in float->str
        conversion of `lon` and `lat`

    Return:
      str: absolute path of destination filename

    """
    # Format lon and lat
    lon = '{lon:0{n}.{decimals}f}{heading}'.format(
        lon=abs(lon),
        n=3 + decimals,
        decimals=decimals,
        heading='W' if lon < 0 else 'E')
    lat = '{lat:0{n}.{decimals}f}{heading}'.format(
        lat=abs(lat),
        n=3 + decimals,
        decimals=decimals,
        heading='S' if lat < 0 else 'N')
    lat_lon = '{lat}_{lon}'.format(lat=lat, lon=lon)

    # Landsat ID -- basename of dirname of source
    landsat_id = os.path.basename(os.path.dirname(os.path.abspath(source)))

    # Filename -- basename of source
    name = os.path.basename(source)
    if ext:
        if ext[0] == '.':
            ext = ext[1:]
        name = '{n}.{e}'.format(n=name, e=ext)

    return os.path.abspath(os.path.join(tile_dir, lat_lon, landsat_id, name))


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
