# -*- coding: utf-8 -*-
""" Export tile dataset to "spewed" data formats
"""
from collections import defaultdict
import logging
import os

import click
import six

from . import cliutils, options
from ..errors import ConsistencyError, ProductNotFoundException
from .._util import include_bands, mkdir_p



@click.command(short_help='Export tile dataset to other dataset format')
@click.option('--bands', multiple=True, type=str,
              callback=options.callback_dict,
              help='Override config file for bands to export into VRT '
                   '(specify using band_attr:pattern)')
@click.option('--regex', is_flag=True,
              help='Allow patterns in `--bands` to be regular expressions')
@click.argument('destination',
                type=click.Path(file_okay=False, resolve_path=True,
                                writable=True))
@click.argument('product_ids', type=int, required=False, nargs=-1,
                callback=options.callback_from_stdin)
@click.pass_context
def spew(ctx, destination, product_ids, bands, regex):
    """ Export tiled products to mutli-band VRTs for a given product ID

    Product IDs can be passed either as input arguments or through `stdin`
    using a pipe.

    By default the configuration file will be used to determine what bands are
    exported into the multi-band VRT format. If `--bands` is specified,
    the configuration file will be ignored and only bands specified by
    `--bands` will be exported.
    """
    config = options.fetch_config(ctx)

    from .. import stores
    logger = logging.getLogger('tilez')
    echoer = cliutils.Echoer(logger)

    echoer.process('Beginning export to VRT for {n} products'
                   .format(n=len(product_ids)))
    spec, storage_name, database, cube, dataset = (
        cliutils.config_to_resources(config))
    mkdir_p(destination)

    if bands:
        include_filter = defaultdict(list)
        for attr, pattern in six.iteritems(bands):
            include_filter[attr].append(pattern)
    else:
        include_filter = config['products']['include_filter'].copy()
        regex = include_filter.pop('regex')

    n_bands = None
    for prod_id in product_ids:
        product = dataset.get_product(prod_id)
        if not product:
            raise ProductNotFoundException('No product in index with ID={}'
                                           .format(prod_id))
        tile = cube.get_tile(database.get_product(prod_id).tile.id)

        echoer.item('Exporting product:\n{0}'
                    .format(str(product).replace('\n', '\n    ')))

        desired_bands = include_bands(product.bands, include_filter, regex)

        n_bands = n_bands or len(desired_bands)
        if len(desired_bands) != n_bands:
            raise ConsistencyError(
                'Inconsistent number of bands found for product '
                '(#{0.id} - {0.timeseries_id}): got {n1} excepted {n2}'
                .format(product, n1=len(desired_bands), n2=n_bands))

        vrt = stores.VRT(*zip(*[(b.src, b.bidx) for b in desired_bands]))
        dest = os.path.join(stores.destination_path(config, tile, product,
                                                    root_override=destination),
                            product.timeseries_id)
        mkdir_p(dest)
        vrt.write(os.path.join(dest,
                               product.timeseries_id + os.extsep + 'vrt'))
