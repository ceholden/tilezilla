# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
from collections import OrderedDict
import fnmatch
import logging
import os

import click
import rasterio

from . import cliutils, options
from .. import products, tilespec
from .._util import decompress_to, multiple_filter
from ..geoutils import reproject_as_needed
from ..stores import GeoTIFFStore

logger = logging.getLogger('tilezilla')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help='Ingest known products into tile dataset format')
@options.arg_sources
@options.opt_tilespec_str
@click.option('--path', envvar='TILEDIR',
              default='/tmp/tilezilla',
              type=click.Path(file_okay=False, writable=True,
                              resolve_path=True),
              help='DEBUG: Put storage here')
@click.pass_context
def ingest(ctx, sources, tilespec_str, path):
    # TODO: add --tilespec-defn (a JSON/YAML config file with tile params)
    # TODO: add --tilespec-[attrs] where [attrs] are tilespec attributes
    if not tilespec_str:
        raise click.UsageError('Must specify a tile specification to use')

    # TODO: user input for bands to save
    include_filter = {
        'long_name': ['*surface reflectance*', '*cfmask*']
    }

    # TODO: config file should describe the basename of tile directories
    # TODO: document choice of where these variables come from (Tile)
    # TODO: parametrize zfill
    tile_root = os.path.join(path, 'h{horizontal:04d}v{vertical:04d}')

    spec = tilespec.TILESPECS[tilespec_str]

    for source in sources:
        echoer.info('Working on: {}'.format(source))

        with decompress_to(source) as tmpdir:
            product = products.registry.sniff_product_type(tmpdir)

            desired_bands = include_bands(product.bands, include_filter)
            for band in desired_bands:
                echoer.process('Tiling: {}'.format(band.long_name))
                with reproject_as_needed(band.src, spec) as src:
                    band.src = src
                    band.band = rasterio.band(src, 1)
                    # from IPython.core.debugger import Pdb; Pdb().set_trace()
                    for tile in spec.bounds_to_tile(src.bounds):
                        tile_path = tile.str_format(tile_root)
                        echoer.item('Saving to: {}'.format(tile_path))

                        store = GeoTIFFStore(tile_path, tile, product)
                        store.store_variable(band, overwrite=True)


def include_bands(bands, include, regex=False):
    """ Include subset of ``bands`` based on ``include``

    Args:
        bands (list[Band]): Bands to filter
        include (dict): Dictionary of 'attribute':['pattern',] used to filter
            input bands for inclusion
        regex (bool): True if patterns in ``include`` are sets of regular
            expressions

    Returns:
        list[Band]: Included bands
    """
    out = []
    for attr in include:
        attrs = OrderedDict(((getattr(b, attr), b) for b in bands))
        match = multiple_filter(attrs.keys(), include[attr], regex=regex)
        out.extend([attrs[k] for k in match])
    return sorted(set(out), key=lambda item: out.index(item))
