# -*- coding: utf-8 -*-i
import errno
import logging
import os

import click
import numpy as np
import rasterio
import rasterio.crs
import rasterio.features
import rasterio.warp
import shapely

from . import cliutils
from . import options
from .. import grids
from .. import utils

logger = logging.getLogger('landsat_tile')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help=u'Subset to 1x1° tile, reproject, and align '
                          'to grid one or more images')
@options.arg_source
@options.arg_tile_dir
@click.option('--grid', default=None, type=click.Choice(grids.grids.keys()),
              help='Use bounds and CRS of a known product')
@click.option('--grid-bounds', nargs=4, type=float, default=None,
              help='Grid bounds: left bottom right top')
@click.option('--grid-crs', default=None,
              help='Grid coordinate reference system.')
@click.option('--grid-res', default=None, nargs=2, type=float,
              help='Grid X/Y resolution')
@click.option('--ext', show_default=True, default=None,
              help='Tile filename extension')
@click.option('--mask', is_flag=True, help=u'Mask output to exactly 1x1°')
@options.opt_nodata
@click.option('--dilate', default=0, type=int, show_default=True,
              help='Number of pixels used to dilate tile bounds when masking')
@options.opt_longitude
@options.opt_latitude
@options.opt_format
@options.opt_creation_options
@click.option('--resampling',
              type=click.Choice(['nearest', 'bilinear', 'cubic','cubic_spline',
                                 'lanczos', 'average', 'mode']),
              default='nearest', show_default=True, help='Resampling method')
@click.option('--threads', type=int, default=1, show_default=True,
              help='Number of processing threads')
@click.option('--no-metadata', 'no_md', is_flag=True,
              help='Do not populate tile images with metadata')
@options.opt_overwrite
@click.pass_context
def tile(ctx, source, tile_dir, ext,
         grid, grid_bounds, grid_crs, grid_res, mask, ndv, dilate, lon, lat,
         driver, creation_options, resampling, threads, overwrite, no_md):
    u""" Subset to 1x1° tile, reproject, and align to grid one or more images

    If --lon and --lat are not specified, the INPUT image will be split into
    all intersecting tiles. Tiles created will be saved under TILE_DIR in
    directories labeled according to the tile location. Directories for a given
    tile will contain tiled images within subdirectories labeled according to
    Landsat ID.

    \b
    Example:
        tiledir/
            41N_072W/
                LT50120312000183AAA02/
                    LT50120312000183AAA02_sr_band1.tif
            41N_073W/
                LT50120312000183AAA02/
                    LT50120312000183AAA02_sr_band1.tif

    Effort is made to copy metadata by setting the metadata on the destination
    image. Metadata come from the source data or source metadata (e.g., MTL
    files) next to input source images. Users can turn off this by specifying
    --no-metadata.

    \b
    TODO:
        1. Copy metadata (see docstring for details)
        2. Benchmark if faster to reproject each band individually, or read all bands in and then reproject

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
        raise click.BadParameter('Invalid CRS format',
                                 param=grid_crs, param_hint=grid['crs'])

    with rasterio.drivers():
        with rasterio.open(source) as src:
            # If --mask, src needs to have a nodata value or user --ndv
            if mask and (src.nodata is None and ndv is None):
                raise click.BadParameter('Cannot mask tiles if INPUT does not '
                                         'have nodata defined. Please override'
                                         ' with --ndv')

            # Find tiles containing sources
            tile_coords = utils.calc_tile_intersection(src.bounds, src.crs)
            if not lon or not lat:
                echoer.info('Calculating intersecting tiles')
            else:
                _user_coords = [(_lon, _lat) for _lon, _lat in zip(lon, lat)]

                # Check provided tiles can exist
                _tile_coords = []
                for _tc in _user_coords:
                    if _tc in tile_coords:
                        _tile_coords.append(_tc)
                    else:
                        echoer.warning('Tile UL {} does not overlap'.
                                       format(_tc))
                tile_coords = tuple(_tile_coords)

            echoer.info('Image intersects with {} tiles'.
                        format(len(tile_coords)))

            # Create all tiles for each source
            echoer.process('Creating image tiles')
            for lon, lat in tile_coords:
                destination = utils.get_tile_output_name(source, tile_dir,
                                                         lon, lat,
                                                         ext=ext,
                                                         decimals=0)

                if os.path.exists(destination) and not overwrite:
                    echoer.item('Already processed tile and not --overwrite. '
                                'Skipping {}'.format(f=(lon, lat)))
                    continue

                try:
                    os.makedirs(os.path.dirname(destination))
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        echoer.error('Error creating destination folder {d}'.
                                     format(d=os.path.dirname(destination)))
                        raise

                echoer.process('Tiling {} to {}'.format((lon, lat),
                                                        destination))

                # Get bounds/transform/size of tile in grid crs
                params = utils.tile_grid_parameters(lon, lat, grid)

                # Configure output metadata
                out_kwargs = src.meta.copy()
                out_kwargs.update({
                    'driver': driver,
                    'crs': grid['crs'],
                    'affine': params['transform'],
                    'transform': params['transform'],
                    'width': params['width'],
                    'height': params['height']
                })
                out_kwargs.update(**creation_options)

                if mask:
                    echoer.item('Masking to exactly tile extent')
                    # Get lat/lon bounding box and reproject to grid CRS
                    mask_geom = rasterio.warp.transform_geom(
                        {'init': 'epsg:4326'},
                        grid['crs'],
                        utils.get_tile_geometry(lon, lat, 1)['geometry'])

                    # Dilate
                    if dilate:
                        buffer_size = dilate * grid['res'][0]
                        echoer.item('Dilating mask of tile extent by {}{}'.
                                    format(buffer_size,
                                           '' or grid['crs']['units']))
                        mask_poly = shapely.geometry.shape(mask_geom)
                        mask_dilate = mask_poly.buffer(buffer_size, 1)
                        mask_geom = shapely.geometry.mapping(mask_dilate)

                    geom_mask = rasterio.features.geometry_mask(
                        (mask_geom, ),
                        (out_kwargs['height'], out_kwargs['width']),
                        out_kwargs['transform'],
                        all_touched=True,
                        invert=False)

                with rasterio.open(destination, 'w', **out_kwargs) as dst:
                    dest_img = np.empty(
                        (out_kwargs['height'], out_kwargs['width']),
                        dtype=src.dtypes[0])

                    for i in range(1, src.count + 1):
                        echoer.item('Reprojecting band {}'.format(i))
                        rasterio.warp.reproject(
                            source=rasterio.band(src, i),
                            destination=dest_img,
                            src_transform=src.affine,
                            src_crs=src.crs,
                            dst_transform=out_kwargs['transform'],
                            dst_crs=out_kwargs['crs'],
                            resampling=resampling,
                            num_threads=threads)

                        if mask:
                            dest_img[geom_mask] = src.nodata or ndv

                        dst.write_band(i, dest_img)
