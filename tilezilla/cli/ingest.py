# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
import logging
import os

import click

from . import cliutils
from . import options
from ..products import registry
from .._util import decompress_to

logger = logging.getLogger('tilezilla')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help='Ingest known products into tile dataset format')
@options.arg_sources
@click.pass_context
def ingest(ctx, sources):
    for source in sources:
        _source = os.path.splitext(os.path.splitext(
                                   os.path.basename(source))[0])[0]
        with decompress_to(source) as tmpdir:
            # Handle archive name as inner folder
            inside_dir = os.listdir(tmpdir)
            if _source in inside_dir:
                tmpdir = os.path.join(tmpdir, _source)

            product = registry.sniff_product_type(tmpdir)
            print(product)
