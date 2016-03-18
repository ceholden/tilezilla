# -*- coding: utf-8 -*-
""" CLI to process imagery products to tiles and index in database
"""
import logging
import os

import click
import rasterio
import six

from . import options
from .cliutils import config_to_resources, Echoer
from .. import products
from .._util import decompress_to, include_bands
from ..errors import FillValueException
from ..geoutils import reproject_as_needed, reproject_bounds
from ..stores import STORAGE_TYPES

logger = logging.getLogger('tilezilla')
echoer = Echoer(message_indent=0)


def ingest_source(config, source, overwrite=False):
    """ Ingest (tile and ingest) a source
    """
    spec = config['tilespec']
    store_name = config['store']['name']
    db = Database.from_config(config['database'])
    datacube = DatacubeResource(db, spec, store_name)
    dataset = DatasetResource(db, datacube)

    # TODO: config file should describe the basename of tile directories
    # TODO: document choice of where these variables come from (Tile)
    # TODO: parametrize zfill
    tile_root = os.path.join(
        config['store']['root'], config['store']['tile_dirpattern'])

    product_filter = config.get('products', {}).get('include_filter', {})
    include_regex = product_filter.pop('regex', False)
    include_filter = product_filter.copy()

    with decompress_to(source) as tmpdir:
        # Find product & select bands
        product = products.registry.sniff_product_type(tmpdir)
        desired_bands = include_bands(
            product.bands, include_filter, regex=include_regex
        )

        # TODO: get bounding_box and reproject to tilespec.crs
        # TODO: next, get tiles before doing anything to bands
        bbox = reproject_bounds(product.bounds, 'EPSG:4326', spec.crs)
        tiles = list(spec.bounds_to_tile(bbox))

        for band in desired_bands:
            with reproject_as_needed(band.src, spec) as src:
                band.src = src
                echoer.item('Tiling: {}'.format(band.long_name))
                for tile in tiles:
                    # Setup dataset store
                    path = tile.str_format(tile_root)
                    store = STORAGE_TYPES[store_name](path, tile, product)
                    # Save and record path
                    try:
                        dst_path = store.store_variable(band)
                    except FillValueException:
                        # TODO: skip tile but complain
                        continue
                    band.path = dst_path
                    # TODO: delete echo
                    echoer.item('    saved to: {}'.format(dst_path))

                    # Index tile and product
                    tile_id = datacube.ensure_tile(product.description,
                                                   tile.horizontal,
                                                   tile.vertical)
                    product_id = dataset.ensure_product(tile_id, product)
                    # Index
                    dataset.ensure_band(product_id, band)
                    # TODO: delete if index went bad

                    # Copy over metadata files
                    for md_name in product.metadata_files:
                        store.store_file(str(product.metadata_files[md_name]))


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
@options.arg_sources
@options.pass_config
@click.pass_context
def ingest(ctx, config, sources):
    for source in sources:
        echoer.info('Working on: {}'.format(source))
        ingest_and_index_source(config, source)
