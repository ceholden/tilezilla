from setuptools import find_packages, setup

# Get version
with open('landsat_tile/version.py') as f:
    for line in f:
        if line.find('__version__') >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

install_requires = [
    'click',
    'click_plugins',
    'numpy',
    'rasterio'
]

entry_points = '''
    [console_scripts]
    landsat_tile=landsat_tile.cli.main:cli

    [landsat_tile.commands]
    unzip=landsat_tile.cli.cli:unzip
    tile=landsat_tile.cli.tile:tile
    prepare=landsat_tile.cli.prepare:prepare
    batch=landsat_tile.cli.cli:batch
'''

setup(
    name='landsat_tile',
    version=version,
    packages=find_packages(),
    package_data={'landsat_tile': ['data/']},
    include_package_data=True,
    install_requires=install_requires,
    entry_points=entry_points
)
