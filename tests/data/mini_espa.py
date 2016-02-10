#!/usr/bin/env python
from contextlib import contextmanager
import fnmatch
import os
import tarfile
import tempfile

import click
import numpy as np
import rasterio
from rasterio import crs
from rasterio.warp import calculate_default_transform, reproject, RESAMPLING


@contextmanager
def temp_expand(filename):
    if os.path.isdir(filename):
        yield filename
    else:
        try:
            tmpdir = tempfile.TemporaryDirectory()
            tarfid = tarfile.open(filename)
            tarfid.extractall(tmpdir.name)
            yield tmpdir.name
        finally:
            tmpdir.cleanup()


@contextmanager
def temp_file():
    try:
        fd, path = tempfile.mkstemp()
        yield path
    finally:
        os.remove(path)


@click.command(short_help='Miniaturize an ESPA download')
@click.argument(
    'source', metavar='INPUT',
    type=click.Path(readable=True, resolve_path=True, dir_okay=True)
)
@click.argument(
    'destination', metavar='DESTINATION',
    type=click.Path(writable=True, exists=False, resolve_path=True,
                    dir_okay=False)
)
@click.option('--offset', nargs=2, type=int, default=(2000, 2000),
              show_default=True, help="x/y offset")
@click.option('--size', nargs=2, type=int, default=(300, 300),
              show_default=True, help="x/y size")
@click.option('--pattern', type=str, default='L*.tif', show_default=True,
              help='Image search pattern')
@click.option('--dst-crs', type=str, help='Target coordinate system')
def miniaturize(source, destination, offset, size, pattern, dst_crs):
    """ Miniaturize an ESPA download
    """
    ox, oy = offset
    sx, sy = size
    window = ((oy, oy + sy), (ox, ox + sx))

    if dst_crs:
        try:
            dst_crs = crs.from_string(dst_crs)
        except ValueError:
            raise click.BadParameter('Invalid crs format',
                                     param=dst_crs, param_hint=dst_crs)

    source_id = os.path.basename(source).split(os.extsep, 1)[0]

    with temp_expand(source) as source:
        sources = sorted([os.path.join(source, f) for f in
                          fnmatch.filter(os.listdir(source), pattern)])
        ancillary = set([os.path.join(source, f) for f in
                         os.listdir(source)]).difference(sources)
        if not sources:
            raise click.ClickException('Cannot find any files in {}'
                                       .format(source))

        with tarfile.open(destination, 'w:gz') as tardest:
            for _anc in ancillary:
                _anc_id = os.path.join(source_id, os.path.basename(_anc))
                tardest.add(_anc, arcname=_anc_id)
                click.echo('Added {} to {}'
                           .format(_anc_id, destination))
            for src in sources:
                src_name = os.path.join(source_id, os.path.basename(src))
                # Copy over window
                with rasterio.open(src, 'r') as src_ds:
                    meta = src_ds.meta.copy()
                    meta.update({
                        'width': sx,
                        'height': sy,
                        'count': 1,
                    })
                    if dst_crs:
                        affine, width, height = calculate_default_transform(
                            src_ds.crs, dst_crs, sx, sy,
                            *src_ds.window_bounds(window),
                            src_ds.res
                        )
                        meta.update({
                            'affine': affine,
                            'transform': affine,
                            'width': width,
                            'height': height,
                            'crs': dst_crs
                        })
                    with temp_file() as dst:
                        with rasterio.open(dst, 'w', **meta) as dst_ds:
                            if dst_crs:
                                reproject(
                                    source=rasterio.band(src_ds, 1),
                                    destination=rasterio.band(dst_ds, 1),
                                    src_transform=src_ds.affine,
                                    src_crs=src_ds.crs,
                                    dst_transform=dst_ds.affine,
                                    dst_crs=dst_ds.crs,
                                    src_nodata=src_ds.nodata,
                                    dst_nodata=dst_ds.nodata,
                                    resampling=RESAMPLING.nearest
                                )
                            else:
                                dst_ds.write_band(
                                    1, src_ds.read(1, window=window))

                        tardest.add(dst, arcname=src_name)
                        click.echo('Added {} to {}'
                                   .format(src_name, destination))
    click.echo('Complete')

if __name__ == '__main__':
    miniaturize()
