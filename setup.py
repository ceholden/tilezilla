import os
from setuptools import find_packages, setup
import sys


PY2 = sys.version_info[0] == 2

# Get version
with open(os.path.join('tilezilla', 'version.py')) as f:
    for line in f:
        if line.find('__version__') >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"').strip("'")
            continue

install_requires = [
    'click',
    'click_plugins',
    'numpy',
    'GDAL',
    'rasterio',
    'shapely',
    'clover',
    'beautifulsoup4',
    'lxml',
    'pyyaml',
    'jsonschema',
    'sqlalchemy',
    'sqlalchemy-utils',
]
if PY2:
    install_requires += ['futures']

entry_points = '''
    [console_scripts]
    tilez=tilezilla.cli.main:cli

    [tilez.commands]
    ingest=tilezilla.cli.ingest:ingest
    spew=tilezilla.cli.spew:spew
    shapes=tilezilla.cli.info:shapes
    db=tilezilla.cli.db:db
'''

setup(
    name='tilezilla',
    version=version,
    packages=find_packages(),
    package_data={'tilezilla': ['data/*']},
    include_package_data=True,
    install_requires=install_requires,
    entry_points=entry_points
)
