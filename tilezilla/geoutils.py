# -*- coding: utf-8 -*-
""" Utilities
"""
import itertools
import json
import logging
from math import ceil
import os

import affine
import numpy as np
import rasterio.coords
import rasterio.crs
import rasterio.warp
import shapely
import shapely.geometry

logger = logging.getLogger('tilezilla')


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


def tile_to_geojson(lon, lat, size=1):
    """ Return a Shapely geometry for a given tile

    Args:
        lon (float): upper left longitude coordinate
        lat (float): upper left latitude coordinate
        size (float or tuple): one or more float values specifying the tile
            size. If one value is specified, tile is assumed to be square.

    Returns:
        dict: tile geometry as GeoJSON dict

    """
    geojson = """
    {
        "geometry":
        {
            "coordinates": [[
                [%s, %s],
                [%s, %s],
                [%s, %s],
                [%s, %s],
                [%s, %s]
            ]],
            "type": "Polygon"
        }
    }
    """ % (lon, lat,                # upper left
           lon + size, lat,         # upper right
           lon + size, lat - size,  # lower right
           lon, lat - size,         # lower left
           lon, lat)                # upper left

    return json.loads(geojson)
