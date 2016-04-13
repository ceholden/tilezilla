# -*- coding: utf-8 -*-
""" CLI to process imagery products to tiles and index in database
"""
import logging
import os

import click

from . import cliutils, options
from .. import multiprocess, products
from .._util import decompress_to, include_bands, mkdir_p
from ..errors import FillValueException
from ..geoutils import reproject_as_needed, reproject_bounds
from ..stores import destination_path, STORAGE_TYPES


def ingest_source(task):
    """ Ingest (tile and ingest) a source
    """
    config, source, overwrite, log_name = task

    mlogger = multiprocess.get_logger_multiproc(name=os.path.basename(source),
                                                filename=log_name)
    echoer = cliutils.Echoer(logger=mlogger)

    spec, storage_name, database, cube, dataset = (
        cliutils.config_to_resources(config))

    product_ids, band_ids = [], []
    echoer.info('Decompressing: {}'.format(os.path.basename(source)))
    with decompress_to(source) as tmpdir:
        # Find product and get dataset database resource
        product = products.registry.sniff_product_type(tmpdir)
        collection_name = product.description

        # Subset bands
        desired_bands = _include_bands_from_config(config, product.bands)

        bbox = reproject_bounds(product.bounds, 'EPSG:4326', spec.crs)

        # Find tiles for product & IDs of these tiles in database
        tiles = list(spec.bounds_to_tiles(bbox))
        tiles_id = [
            cube.ensure_tile(
                collection_name, tile.horizontal, tile.vertical)
            for tile in tiles
        ]
        tiles_product_query = [
            database.get_product_by_name(tile_id, product.timeseries_id)
            for tile_id in tiles_id
        ]

        for band in desired_bands:
            echoer.info('Reprojecting band: {}'.format(band))
            with reproject_as_needed(band.src, spec) as src:
                band.src = src
                echoer.process('Tiling: {}'.format(band.long_name))
                for tile, tile_id, tile_prod_query in zip(tiles,
                                                          tiles_id,
                                                          tiles_product_query):
                    # Check if exists
                    if tile_prod_query:
                        _band_names = [b.standard_name for b in
                                       tile_prod_query.bands]
                        if band.standard_name in _band_names and not overwrite:
                            echoer.item('Already tiled -- skipping')
                            continue

                    # Setup dataset store
                    path = destination_path(config, tile, product)
                    store_cls = STORAGE_TYPES[config['store']['name']]
                    store = store_cls(path, tile,
                                      meta_options=config['store']['co'])

                    # Save and record path
                    try:
                        dst_path = store.store_variable(product, band,
                                                        overwrite=overwrite)
                    except FillValueException:
                        # TODO: skip tile but complain
                        continue
                    band.path = dst_path

                    # Copy over metadata files
                    for md_name in product.metadata_files:
                        dst_path = store.store_file(
                            product, str(product.metadata_files[md_name]))
                        product.metadata_files[md_name] = dst_path

                    # Update index with new product/band entry
                    if tile_prod_query:
                        # TODO: we need to handle deleting/transfering existing
                        #       bands over maybe overwriting product
                        product_id = tile_prod_query.id
                        band_id = dataset.update_band(tile_prod_query.id, band)
                    else:
                        product_id = dataset.ensure_product(tile_id, product)
                        band_id = dataset.ensure_band(product_id, band)

                    # TODO: delete file if index went bad
                    product_ids.append(product_id)
                    band_ids.append(band_id)

                    echoer.item('Tiled band for tile h{}v{}'
                                .format(tile.horizontal, tile.vertical))

    return set(product_ids), set(band_ids)


def _include_bands_from_config(config, bands):
    """ Return a list of :class:`Band`s specified in tilezilla configuration

    Args:
        config (dict): `tilezilla` configuration
        bands (list[Band]): List of bands to filter

    Returns:
        list[Bands]: Included bands
    """
    # TODO: move elsewhere
    product_filter = (config.get('products', {}).copy()
                      .get('include_filter', {}))
    include_regex = product_filter.pop('regex', False)

    return include_bands(bands, product_filter, regex=include_regex)


@click.command(short_help='Ingest known products into tile dataset format')
@options.opt_multiprocess_method
@options.opt_multiprocess_njob
@click.option('--log_dir', 'log_dir',
              type=click.Path(exists=False, dir_okay=True, writable=True,
                              resolve_path=True),
              help='Log ingests to this directory (otherwise to stdout)')
@click.option('--overwrite', is_flag=True,
              help='Overwriting existing tiled data')
@options.arg_sources
@click.pass_context
def ingest(ctx, sources, overwrite, log_dir, njob, parallel):
    config = options.fetch_config(ctx)
    logger = logging.getLogger('tilez')
    echoer = cliutils.Echoer(logger)

    echoer.info('Ingesting {} products'.format(len(sources)))
    if log_dir:
        mkdir_p(log_dir)

    tasks = [(config, src, overwrite, log_dir and
              os.path.join(log_dir, os.path.basename(src) + '.log'))
             for src in sources]

    results = parallel.map(ingest_source, tasks)

    product_ids = []
    band_ids = []
    for result in results:
        product_ids.extend(result[0])
        band_ids.extend(result[1])

    echoer.process('Indexed {nprod} products to {ntile} tiles of {nband} bands'
                   .format(nprod=len(sources),
                           ntile=len(set(product_ids)),
                           nband=len(band_ids)))
