#!/bin/bash

project=landsat_tile

cd $(dirname $0)

rm source/$project/*.rst
make clean

cd ../

sphinx-apidoc -f -e -o docs/source/$project/ $project/

cd docs
make html
