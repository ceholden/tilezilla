#!/bin/bash
#$ -V
#$ -l h_rt=24:00:00
#$ -l eth_speed=10
#$ -j y
#$ -N make_tile

set +e

tiledir=$1
if [ -z $1 ]; then
    echo "Must specify tiledir as 1st input arg"
    exit 1
fi

imgs=$(find images -name 'L*stack')
n=$(echo "$imgs" | wc -w)

i=1
for img in $imgs; do
    echo "$i / $n: Working on $img"
    landsat_tile -v tile --ext .gtif --grid nlcd1992 \
        --co COMPRESS=LZW \
        --mask \
        $img $tiledir
    let i+=1
done

echo "Complete"
