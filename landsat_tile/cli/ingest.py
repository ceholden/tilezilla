# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
import logging

import click

from . import cliutils

logger = logging.getLogger('landsat_tile')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help='Ingest known products into tile dataset format')
@click.pass_context
def ingest(ctx):
    pass
