#!/usr/bin/env python
from contextlib import contextmanager
import fnmatch
import os
import tarfile
import tempfile

import click
import rasterio


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
def miniaturize(source, destination, offset, size, pattern):
    """ Miniaturize an ESPA download
    """
    ox, oy = offset
    sx, sy = size

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
                    meta = src_ds.meta
                    meta.update({
                        'width': sx,
                        'height': sy,
                        'count': 1,
                    })
                    with temp_file() as dst:
                        with rasterio.open(dst, 'w', **meta) as dst_ds:
                            _dst = src_ds.read(1, window=((oy, oy + sy),
                                                          (ox, ox + sx)))
                            dst_ds.write_band(1, _dst)
                        # from IPython.core.debugger import Pdb; Pdb().set_trace()
                        # info = tardest.gettarinfo(dst, arcname=src_name)
                        # tardest.addfile(info)
                        tardest.add(dst, arcname=src_name)
                        click.echo('Added {} to {}'
                                   .format(src_name, destination))
    click.echo('Complete')

if __name__ == '__main__':
    miniaturize()
