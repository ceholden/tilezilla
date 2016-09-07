.. _guide_spew:

VRT Export
==========

Tilezilla stores tiled data in a flexible and extendible manner so that
additional data, including additional bands for the same acquisition, may be
indexed and added. This storage arrangement, however, is not always ideal for
analysis in existing codebases.

The ``tilez spew`` program was written to convert the storage systems used in
Tilezilla (e.g., GeoTIFF) into something more familiar. Specifically,
`tilez spew` will create multi-band Virtual Raster dataset (VRT) for each
acquisition containing a collection of bands desired by the user. VRTs should
ease the use of time series of imagery ingested by Tilezilla because the VRTs
bundle multiple bands together.

.. code-block:: bash

    $ tilez spew -h
    Usage: tilez spew [OPTIONS] DESTINATION [PRODUCT_IDS]...

      Export tiled products to mutli-band VRTs for a given product ID

      Product IDs can be passed either as input arguments or through `stdin`
      using a pipe.

      By default the configuration file will be used to determine what bands are
      exported into the multi-band VRT format. If `--bands` is specified, the
      configuration file will be ignored and only bands specified by `--bands`
      will be exported.

    Options:
      --bands TEXT  Override config file for bands to export into VRT (specify
                    using band_attr:pattern)
      --regex       Allow patterns in `--bands` to be regular expressions
      -h, --help    Show this message and exit.

Example
-------

To begin, the ``spew`` command needs to know what products in the database to
convert to the VRT format.

.. code-block:: bash

    > tilez db id --filter "n_bands = 8" --filter "acquired > 2000-01-01" --filter "acquired < 2016-01-01" product
    9

Note that we use the command ``tilez db id`` as a proxy for
``tilez db info --quiet --select id`` and can include search filter options
using the ``--filter`` flag. For more information on searching the database for
ingested products, see :ref:`guide_cli_db`.

The fastest way of exporting the products found during a search into VRT format
is to use the Unix pipe:

.. code-block:: bash

    > tilez db id --filter "n_bands = 8" --filter "acquired > 2000-01-01" --filter "acquired < 2016-01-01" product | tilez -v spew VRTs/
    11:18:58:INFO:==> Beginning export to VRT for 9 products
    11:18:58:INFO:-       Exporting product: LT50120312002300LGS01
    11:18:58:INFO:-           Friendly band names: sr_band1, sr_band2, sr_band3, sr_band4, sr_band5, sr_band7, toa_band6, cfmask
    ...
    11:18:58:INFO:-       Exporting product: LT50120312002300LGS01
    11:18:58:INFO:-           Friendly band names: sr_band1, sr_band2, sr_band3, sr_band4, sr_band5, sr_band7, toa_band6, cfmask


Once complete, the command has created 9 VRTs that reference 72 product bands
(9 tiled products x 8 bands/product) and organized them into the same
hierarchical structure used to store the tiled data (e.g., by product, tile
reference, and product ID):

.. code-block:: bash

    > tree VRTs/
    > VRTs
    └── ESPALandsat
        ├── h0029v0005
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0029v0006
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0029v0007
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0030v0005
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0030v0006
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0030v0007
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0031v0005
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        ├── h0031v0006
        │   └── LT50120312002300LGS01
        │       └── LT50120312002300LGS01.vrt
        └── h0031v0007
            └── LT50120312002300LGS01
                └── LT50120312002300LGS01.vrt

Each of these VRTs contains the 8 bands specified by the configuration file
``include_filter`` option for the ``ESPALandsat`` product. As such, a
``gdalinfo`` reveals the structure as:

.. code-block:: bash

    > gdalinfo VRTs/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01.vrt
    Driver: VRT/Virtual Raster
    Files: VRTs/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01.vrt
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band1.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band2.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band3.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band4.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band5.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_sr_band7.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_toa_band6.tif
           /home/ceholden/tiles/ESPALandsat/h0029v0005/LT50120312002300LGS01/LT50120312002300LGS01_cfmask.tif
    Size is 5000, 5000
    Coordinate System is:
    PROJCS["NAD83 / Conus Albers",
        GEOGCS["NAD83",
            DATUM["North_American_Datum_1983",
                SPHEROID["GRS 1980",6378137,298.257222101,
                    AUTHORITY["EPSG","7019"]],
                TOWGS84[0,0,0,0,0,0,0],
                AUTHORITY["EPSG","6269"]],
            PRIMEM["Greenwich",0,
                AUTHORITY["EPSG","8901"]],
            UNIT["degree",0.0174532925199433,
                AUTHORITY["EPSG","9122"]],
            AUTHORITY["EPSG","4269"]],
        PROJECTION["Albers_Conic_Equal_Area"],
        PARAMETER["standard_parallel_1",29.5],
        PARAMETER["standard_parallel_2",45.5],
        PARAMETER["latitude_of_center",23],
        PARAMETER["longitude_of_center",-96],
        PARAMETER["false_easting",0],
        PARAMETER["false_northing",0],
        UNIT["metre",1,
            AUTHORITY["EPSG","9001"]],
        AXIS["X",EAST],
        AXIS["Y",NORTH],
        AUTHORITY["EPSG","5070"]]
    Origin = (1784400.000000000000000,2564800.000000000000000)
    Pixel Size = (30.000000000000000,-30.000000000000000)
    Corner Coordinates:
    Upper Left  ( 1784400.000, 2564800.000) ( 73d24'28.78"W, 44d 9'21.00"N)
    Lower Left  ( 1784400.000, 2414800.000) ( 73d50'33.58"W, 42d50'56.42"N)
    Upper Right ( 1934400.000, 2564800.000) ( 71d35'17.96"W, 43d49'35.62"N)
    Lower Right ( 1934400.000, 2414800.000) ( 72d 3'18.28"W, 42d31'35.86"N)
    Center      ( 1859400.000, 2489800.000) ( 72d43'24.65"W, 43d20'32.69"N)
    Band 1 Block=128x128 Type=Int16, ColorInterp=Blue
      NoData Value=-9999
    Band 2 Block=128x128 Type=Int16, ColorInterp=Green
      NoData Value=-9999
    Band 3 Block=128x128 Type=Int16, ColorInterp=Red
      NoData Value=-9999
    Band 4 Block=128x128 Type=Int16, ColorInterp=Undefined
      NoData Value=-9999
    Band 5 Block=128x128 Type=Int16, ColorInterp=Undefined
      NoData Value=-9999
    Band 6 Block=128x128 Type=Int16, ColorInterp=Undefined
      NoData Value=-9999
    Band 7 Block=128x128 Type=Int16, ColorInterp=Undefined
      NoData Value=-9999
    Band 8 Block=128x128 Type=Byte, ColorInterp=Undefined
      NoData Value=255

One could also manually specify the bands to include in the VRT images
manually using the `--bands` option:

.. code-block:: bash

    > tilez -v spew --bands long_name="*surface reflectance*" SR_VRTS 1
    11:20:20:INFO:==> Beginning export to VRT for 1 products
    11:20:20:INFO:-       Exporting product: LT50120312002300LGS01
    11:20:20:INFO:-           Friendly band names: sr_band1, sr_band2, sr_band3, sr_band4, sr_band5, sr_band7
