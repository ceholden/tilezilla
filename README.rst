tilezilla (a WIP)
=================

|Build Status| |Coverage| |Docs|

STATUS: IN REDEVELOPMENT
------------------------

About
-----

Ingest remote sensing products (e.g., Landsat Climate Data Record (CDR) by USGS) into tiled datasets in a common projection suitable for large scale analysis beyond traditional WRS-2
path and row or UTM zone boundaries. Input images can be reprojected into a suitable projection and grid to mimic pre-existing products (e.g., `National Land Cover Database
(NLCD) <http://www.mrlc.gov/index.php>`__) or users can define their own projection and grid. Timeseries assembled from such tiles can easily incorporate observations from multiple viewing geometries by taking advantage of "sidelap" areas in adjacent WRS-2 paths.

Demo (OUTDATED)
---------------

As a demonstration of this project's output, I tiled a layer stacked Landsat 5 image over Boston:

.. code:: bash

    $ tilezilla tile --grid nlcd1992 --mask --threads 4 --co "COMPRESS=LZW" LT50120312000183AAA02/LT50120312000183AAA02_stack.tif tiles/
    *   Calculating intersecting tiles
    *   Image intersects with 12 tiles
    ==> Creating image tiles
    ==> Tiling (-73.0, 41.0) to /home/ceholden/Documents/tilezilla/tiles/041N_073W/LT50120312000183AAA02/LT50120312000183AAA02_stack.tif
    -   Masking to exactly tile extent
    -   Reading in input image
    -   Reprojecting all bands in image
    ...
    ==> Tiling (-70.0, 43.0) to /home/ceholden/Documents/tilezilla/tiles/043N_070W/LT50120312000183AAA02/LT50120312000183AAA02_stack.tif
    -   Masking to exactly tile extent
    -   Reading in input image
    -   Reprojecting all bands in image

I opened the original image, the image tiles, and vector files that show the outline of the tiles created in QGIS as a demonstration:

.. figure:: ./docs/examples/demo.gif
   :alt: Demo

   Demo

Usage
-----

``tilezilla`` contains several sub-commands that either help coordinate the tiling process (``batch``, ``prepare``, ``unzip``, and more) or actually perform the image tiling (``tile``). Currently, only the ``tile`` sub-command is implemented.

The full usage is:

.. code:: bash

    $ Usage: tilezilla [OPTIONS] COMMAND [ARGS]...

      Landsat tile preprocessing command line interface (CLI)

    Options:
      --version      Show the version and exit.
      -v, --verbose  Be verbose
      -q, --quiet    Be quiet
      -h, --help     Show this message and exit.

    Commands:
      ingest  Ingest known products into tile dataset format
      shapes  Get shapes of tiled datasets
      spew    Export tile dataset to other dataset format

Installation
------------

Anaconda
~~~~~~~~

The easiest way to install ``tilezilla`` is to use the conda_ package manager from the `Anaconda project <https://www.continuum.io/why-anaconda>`__ by `Continuum Analytics <https://www.continuum.io/>`__. You can grab ``conda`` either through the full ``Anaconda`` installer or using the ``miniconda`` installer from their `downloads page <https://www.continuum.io/downloads>`__.

With ``conda`` installed, you can install all dependendies of ``tilezilla`` into an isolated environment using the ``conda env`` subcommand:

.. code:: bash

    # Create environment
    $ conda env create -f environment.yaml
    # Activate environment
    $ source activate tilezilla
    # Install tilezilla
    $ pip install .

Development
~~~~~~~~~~~

If you are interested in developing ``tilezilla``, I suggest installing via ``pip`` with the ``-e`` flag to create an editable installation. For installation instructions for developing ``tilezilla`` using the click_ command line interface library, see `click's setuptools installation instructions <http://click.pocoo.org/5/setuptools/>`__.


.. |Build Status| image:: https://travis-ci.org/ceholden/tilezilla.svg?branch=master
   :target: https://travis-ci.org/ceholden/tilezilla
.. |Coverage| image:: https://coveralls.io/repos/github/ceholden/tilezilla/badge.svg?branch=master
   :target:  https://coveralls.io/github/ceholden/tilezilla?branch=master
.. |Docs| image:: https://readthedocs.org/projects/tilezilla/badge/?version=latest
   :target: http://tilezilla.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status
.. _click: http://click.pocoo.org/
.. _conda: http://conda.pydata.org/docs/
