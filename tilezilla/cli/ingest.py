# -*- coding: utf-8 -*-
""" CLI to process imagery products to tiles and index in database
"""
from collections import defaultdict
import concurrent.futures
import logging
import os

import click
import six

# TODO: hide many of these imports to improve CLI startup speed
from . import cliutils, options
from .. import multiprocess, products
from .._util import decompress_to, include_bands, mkdir_p
from ..errors import FillValueException
from ..geoutils import reproject_as_needed, reproject_bounds
from ..stores import destination_path, STORAGE_TYPES


def ingest_source(config, source, overwrite, log_name):
    """ Ingest (tile and index) a source

    Table entries for indexing are created and returned by this function so
    that database writes can be performed in parent process/context.
    """
    mlogger = multiprocess.get_logger_multiproc(name=os.path.basename(source),
                                                filename=log_name)
    echoer = cliutils.Echoer(logger=mlogger)

    spec, storage_name, database, cube, dataset = (
        cliutils.config_to_resources(config))

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
        tiles_product = {
            tile_id: database.get_product_by_name(
                tile_id, product.timeseries_id)
            for tile_id in tiles_id
        }

        indexed_products, indexed_bands = {}, defaultdict(list)
        for band in desired_bands:
            echoer.info('Reprojecting band: {}'.format(band))
            with reproject_as_needed(band.src, spec) as src:
                band.src = src
                echoer.process('Tiling: {}'.format(band.long_name))
                for tile, tile_id in zip(tiles, tiles_id):
                    db_product = tiles_product[tile_id]
                    if db_product:
                        # If product is in DB, check if we have bands to add
                        _band_names = [b.standard_name for b
                                       in db_product.bands]
                        if band.standard_name in _band_names and not overwrite:
                            echoer.item('Already tiled -- skipping')
                            continue
                    else:
                        # Product not in DB -- need to create
                        db_product = database.create_product(product)
                        db_product.ref_tile_id = tile_id
                        tiles_product[tile_id] = db_product

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
                    for md_name, md_file in six.iteritems(
                            product.metadata_files):
                        if md_file:
                            dst_path = store.store_file(product, md_file)
                            product.metadata_files[md_name] = dst_path

                    # Update index with new product/band entry
                    if db_product.id:
                        db_band = (
                            database.get_band_by_name(db_product.id,
                                                      band.standard_name)
                            or database.create_band(band)
                        )
                    else:
                        db_product = database.create_product(product)
                        db_product.ref_tile_id = tile_id
                        db_band = database.create_band(band)

                    indexed_products[tile_id] = db_product
                    indexed_bands[tile_id].append(db_band)

                    # TODO: delete file if index went bad
                    echoer.item('Tiled band for tile {}'.format(
                        tile.str_format(config['store']['tile_dirpattern'])
                    ))

    # Make sure to close database connection
    database.session.close()
    return indexed_products, indexed_bands


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
def ingest(ctx, sources, overwrite, log_dir, njob, executor):
    config = options.fetch_config(ctx)
    logger = logging.getLogger('tilez')
    echoer = cliutils.Echoer(logger)

    spec, storage_name, database, cube, dataset = (
        cliutils.config_to_resources(config))

    echoer.info('Ingesting {} products'.format(len(sources)))
    if log_dir:
        mkdir_p(log_dir)

    product_ids, band_ids = [], []
    futures = {
        executor.submit(ingest_source, config, src, overwrite,
                        log_dir and os.path.join(
                            log_dir, os.path.basename(src) + '.log')): src
        for src in sources
    }

    sources_indexed = 0
    for future in concurrent.futures.as_completed(futures):
        src = futures[future]
        try:
            indexed_products, indexed_bands = future.result()
            for k in indexed_products:
                prod = indexed_products[k]
                with database.scope() as txn:
                    txn.merge(prod) if prod.id else txn.add(prod)
                    txn.flush()
                    for b in indexed_bands[k]:
                        b.ref_product_id = prod.id
                        txn.merge(b) if b.id else txn.add(b)
                product_ids.append(prod.id)
                band_ids.extend([b.id for b in indexed_bands[k]])
        except Exception as exc:
            echoer.warning('Ingest of {} produced exception: {}'
                           .format(src, exc))
        else:
            echoer.item('Ingested: {} (product IDs: {})'
                        .format(src, [p.id for p in indexed_products.values()])
            )
            sources_indexed += 1

    echoer.process('Indexed {nprod} products to {ntile} tiles of {nband} bands'
                   .format(nprod=sources_indexed,
                           ntile=len(set(product_ids)),
                           nband=len(band_ids)))
