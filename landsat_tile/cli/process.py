# -*- coding: utf-8 -*-
""" Process an image or compressed tarball of images to tiles
"""
import logging

import click

from . import cliutils
from . import options
from .. import tilespec


logger = logging.getLogger('landsat_tile')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help=u'Create tiless from an image or archive of images')
@options.opt_longitude
@options.opt_latitude
@click.option('--threads', type=int, default=1, show_default=True,
              help='Number of processing threads')
@options.opt_overwrite
@click.pass_context
def process(ctx, lon, lat, threads, overwrite):
    u""" TODO
    """
    echoer.process('TODO')
