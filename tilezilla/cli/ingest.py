# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
import fnmatch
import logging
import os

import click
import rasterio

from . import cliutils, options
from .. import products, tilespec
from .._util import decompress_to, mkdir_p
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

    spec = tilespec.TILESPECS[tilespec_str]

    for source in sources:
        echoer.info('Working on: {}'.format(source))
        _source = os.path.splitext(os.path.splitext(
                                   os.path.basename(source))[0])[0]
        with decompress_to(source) as tmpdir:
            # Handle archive name as inner folder
            inside_dir = os.listdir(tmpdir)
            if _source in inside_dir:
                tmpdir = os.path.join(tmpdir, _source)

            product = products.registry.sniff_product_type(tmpdir)
            desired_bands = include_bands(product.bands, include_filter)
            for band in desired_bands:
                with reproject_as_needed(band.src, spec) as src:
                    band.src = src
                    band.band = rasterio.band(src, 1)
                    # from IPython.core.debugger import Pdb; Pdb().set_trace()
                    for tile in spec.bounds_to_tile(src.bounds):
                        _path = os.path.join(path, 'y{}_x{}'.format(
                            tile.index[0], tile.index[1]))
                        mkdir_p(_path)
                        store = GeoTIFFStore(_path, tile, product)
                        store.store_variable(band, overwrite=True)
                    print("To be continued... {}".format(src))


def include_bands(bands, include):
    """ Include subset of ``bands`` based on ``include``

    Args:
        bands (list[Band]): Bands to filter
        include (dict): Dictionary of 'attribute':['pattern',] used to filter
            input bands for inclusion

    Returns:
        list[Band]: Included bands
    """
    out = set()
    for attr in include:
        for pattern in include[attr]:
            for b in bands:
                if fnmatch.filter([getattr(b, attr)], pattern):
                    out.add(b)
    return out
