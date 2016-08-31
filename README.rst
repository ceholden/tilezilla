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

Demo
---------------

As a demonstration of this project's output, I tiled a layer stacked Landsat 5 image over Boston:

.. code:: bash

    $ tilez -C sandbox/demo_ingest.yaml ingest -pe process -j 4 tests/data/L*tar.gz
    11:44:39:INFO:*   Ingesting 5 products
    11:44:39:ceholden-ldesk:4762:INFO:*   Decompressing: LT40130301987146-SC20151019150137.tar.gz
    11:44:39:ceholden-ldesk:4760:INFO:*   Decompressing: LE70130301999195-SC20151019134154.tar.gz
    11:44:39:ceholden-ldesk:4763:INFO:*   Decompressing: LT50120312002300-SC20151009172149.tar.gz
    11:44:39:ceholden-ldesk:4761:INFO:*   Decompressing: LE70130312015175-SC20151019173810.tar.gz
    11:44:39:ceholden-ldesk:4761:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dbaabbc18>
    11:44:39:ceholden-ldesk:4763:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dbaa55400>
    11:44:39:ceholden-ldesk:4760:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dbaabbcf8>
    11:44:39:ceholden-ldesk:4762:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dbaab9b00>
    11:44:39:ceholden-ldesk:4760:INFO:==> Tiling: band 1 surface reflectance
    11:44:39:ceholden-ldesk:4763:INFO:==> Tiling: band 1 surface reflectance
    11:44:39:ceholden-ldesk:4761:INFO:==> Tiling: band 1 surface reflectance
    11:44:39:ceholden-ldesk:4762:INFO:==> Tiling: band 1 surface reflectance
    11:44:40:ceholden-ldesk:4760:INFO:-       Tiled band for tile h0029v0005
    11:44:40:ceholden-ldesk:4763:INFO:-       Tiled band for tile h0029v0006
    11:44:40:ceholden-ldesk:4760:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dbaabbe10>
    11:44:40:ceholden-ldesk:4762:INFO:-       Tiled band for tile h0029v0005
    11:44:40:ceholden-ldesk:4761:INFO:-       Tiled band for tile h0029v0006
    ...
    11:44:52:ceholden-ldesk:4760:INFO:*   Reprojecting band: <tilezilla.core.Band object at 0x7f7dba9d29e8>
    11:44:52:ceholden-ldesk:4760:INFO:==> Tiling: cfmask_band
    11:44:52:ceholden-ldesk:4760:INFO:-       Tiled band for tile h0029v0005
    11:44:52:INFO:-       Ingested: /home/ceholden/Documents/tilezilla/tests/data/LT50130301994205-SC20151019145346.tar.gz (product IDs: [6])
    11:44:52:INFO:==> Indexed 5 products to 6 tiles of 48 bands

I opened the original image, the image tiles, and vector files that show the outline of the tiles created in QGIS as a demonstration:

.. figure:: ./docs/examples/demo.gif
   :alt: Demo

   Demo

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
