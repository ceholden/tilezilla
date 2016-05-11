# TODO

## Maintenance
* [ ] Move ingest logic into separate module outside of CLI
    * Benefits:
        1. Easier to re-use in other applications
        2. Easier to split up logic
        3. Easier to test
        4. Helps reduce startup cost for `tilez` CLI

## CLI
* [ ] Hide all heavy imports into command functions
    * Look to how `rasterio` accomplishes it
* `tilez db`
    * [x] Translate search from CLI optargs to `sqlalchemy` queries
    * [ ] Search based on well defined table metadata
    * [ ] Search based on less well defined table metadata
        * [x] Search meta-attributes
            * [x] `n_bands`
        * [ ] Search `metadata_` JSONs
    * [ ] Search based on geographic

## API
* Steps:
    * [ ] Init API with singular tile specification
    * [ ] Select a collection of products (e.g., ESPA)
    * [ ] Search for tiles using an extent
        * [ ] Initially, just read 1 tile and NDV-pad outside tile
        * [ ] Eventually, stich across tiles
    * [ ] Search for products matching defined metadata
    * [ ] Select bands to return as variables in `xarray` dataset

## Stores:
* [x] GeoTIFF format
* [x] "Spew" to VRT
* [ ] NetCDF storage

## Products
* [ ] ESPA
    * [x] Remove MTL file requirement
    * [ ] Handle two types of HDF formats: HDF pointing to .img files & HDF containing data internally

## Config:
* [x] Allow `tilez ingest --help` to work without providing a config file
* [x] Pass config via arg rather than context
* [x] Reprojection options
