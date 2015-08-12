# -*- coding: utf-8 -*-
import logging
from math import ceil

import click
import numpy as np
import rasterio
import rasterio.rio.options

from . import options
from .. import grids
from .. import utils

logger = logging.getLogger('landsat_tile')


@click.command(short_help=u'Subset to 1x1° tile, reproject, and align '
                          'to grid one or more images')
@options.arg_source
@options.arg_destination
@click.option('--grid', default=None, type=click.Choice(grids.grids.keys()),
              help='Use bounds and CRS of a known product')
@click.option('--grid-bounds', nargs=4, type=float, default=None,
              help='Grid bounds: left bottom right top')
@click.option('--grid-crs', default=None,
              help='Grid coordinate reference system.')
@click.option('--grid-res', default=None, nargs=2, type=float,
              help='Grid X/Y resolution')
@click.option('--mask', is_flag=True, help=u'Mask output to exactly 1x1°')
@click.option('--dilate', default=10, type=int, show_default=True,
              help='Number of pixels used to dilate tile bounds')
@options.opt_longitude
@options.opt_latitude
@options.opt_format
@rasterio.rio.options.creation_options
@click.option('--resampling',
              type=click.Choice(['nearest', 'bilinear', 'cubic',
                                 'cubic_spline','lanczos', 'average', 'mode']),
              default='nearest', show_default=True, help='Resampling method')
@click.option('--threads', type=int, default=1, show_default=True,
              help='Number of processing threads')
@options.opt_overwrite
@click.pass_context
def tile(ctx, sources, destination,
         grid, grid_bounds, grid_crs, grid_res, dilate, lon, lat,
         driver, creation_options, resampling, threads, overwrite):
    u""" Subset to 1x1° tile, reproject, and align to grid one or more images

    Input images, if multiple are specified, must be the same pixel resolution,
    shape, and coordinate extent.

    \b
    TODO:
        1. Change docstring/title/etc
        2. Ability to loop over lon/lat
        3. If no lon/lat specified, find all that intersect

    """
    resampling = getattr(rasterio.warp.RESAMPLING, resampling)

    # Handle grid definition
    if not grid and not (grid_bounds and grid_crs and grid_res):
        raise click.UsageError(
            'Must specify either --grid or provide values for '
            '--grid-bounds, --grid-crs and --grid-res')

    if grid:
        grid = grids.grids[grid]
    else:
        grid = {}
        grid['bounds'] = grid_bounds
        grid['crs'] = grid_crs
        grid['res'] = grid_res

    try:
        grid['crs'] = rasterio.crs.from_string(grid['crs'])
    except ValueError:
        raise click.BadParameter('invalid CRS format',
                                 param=grid_crs, param_hint=grid['crs'])

    with rasterio.open(sources[0], 'r') as first:
        meta = first.meta.copy()

        if not lon or not lat:
            logger.debug('Tile lon/lat not provided -- calculating tiles')
            # Find tiles containing sources

        else:
            from IPython.core.debugger import Pdb
            Pdb().set_trace()
            logger.debug('Tiling to ')


    # Formulate tile bounds
    tile_bounds_lonlat = rasterio.coords.BoundingBox(left=lon, bottom=lat - 1,
                                                     right=lon + 1, top=lat)

    # Reproject tile bounds to grid CRS
    # NOTE: transform_bounds doesn't seem to work... do it manually
    xs, ys = rasterio.warp.transform(
        {'init': 'epsg:4326'}, grid['crs'],
        [lon, lon, lon + 1, lon + 1],
        [lat, lat - 1, lat, lat - 1])
    tile_bounds = rasterio.coords.BoundingBox(
        left=min(xs), bottom=min(ys), right=max(xs), top=max(ys))

    # Co-register reprojected tile bounds to grid
    xmin, ymin, xmax, ymax = rasterio.coords.BoundingBox(
        *utils.match_to_grid(tile_bounds, grid['bounds'], grid['res'] * 2))
    logger.debug('Tile coordinates: {bbox}'.format(
        bbox=rasterio.coords.BoundingBox(xmin, ymin, xmax, ymax)))

    grid['bounds'] = rasterio.coords.BoundingBox(xmin, ymin, xmax, ymax)
    logger.debug('Tile coordinates after dilate: {}'.format(grid['bounds']))

    # Create affine transform and height/width
    grid['transform'] = rasterio.Affine(grid['res'][0], 0, xmin,
                                        0, -grid['res'][1], ymax)
    grid['width'] = max(int(ceil((xmax - xmin) / grid['res'][0])), 1)
    grid['height'] = max(int(ceil((ymax - ymin) / grid['res'][1])), 1)

    with rasterio.drivers():
        with rasterio.open(source) as src:
            # Configure output metadata
            out_kwargs = src.meta.copy()
            out_kwargs.update({
                'driver': driver,
                'crs': grid['crs'],
                'affine': grid['transform'],
                'transform': grid['transform'],
                'width': grid['width'],
                'height': grid['height']
            })
            out_kwargs.update(**creation_options)

            # Ensure source data in tile
            src_bounds = rasterio.warp.transform_bounds(
                src.crs, out_kwargs['crs'], *src.bounds)
            if not utils.intersects_bounds(grid['bounds'], src_bounds):
                raise click.ClickException(
                    'Input image (center lon/lat: {0}) does not '
                    'intersect tile with lon/lat bounds '
                    '{1}'.format(src.lnglat(), tile_bounds_lonlat))

            with rasterio.open(destination, 'w', **out_kwargs) as dst:
                for i in range(1, src.count + 1):
                    rasterio.warp.reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.affine,
                        src_crs=src.crs,
                        dst_transform=out_kwargs['transform'],
                        dst_crs=out_kwargs['crs'],
                        resampling=resampling,
                        num_threads=threads)

