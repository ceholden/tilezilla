# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
import logging
import os

import click

from . import cliutils, options
from .. import products, tilespec
from .._util import decompress_to, mkdir_p
from ..geoutils import reproject_as_needed
from ..store import GeoTIFFStore

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
            for band in product.bands:
                with reproject_as_needed(band.src, spec) as src:
                    # from IPython.core.debugger import Pdb; Pdb().set_trace()
                    for tile in spec.bounds_to_tile(src.bounds):
                        _path = os.path.join(path, 'y{}_x{}'.format(
                            tile.index[0], tile.index[1]))
                        mkdir_p(_path)
                        store = GeoTIFFStore(_path, tile, product)
                        store.store_variable(band, src=src, overwrite=True)
                    print("To be continued... {}".format(src))
