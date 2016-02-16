# -*- coding: utf-8 -*-
""" Export tile dataset to "spewed" data formats
"""
import logging

import click

from . import cliutils

logger = logging.getLogger('tilezilla')
echoer = cliutils.Echoer(message_indent=0)


@click.command(short_help='Export tile dataset to other dataset format')
@click.pass_context
def spew(ctx):
    pass
