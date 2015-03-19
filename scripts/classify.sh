#!/bin/bash

# Arguments:  directory, slope, cellsize

FILENAMES=$1/*.las

date
echo "File count = " `ls -1 *.las | wc -l`

for FNAME in $FILENAMES; do
    # run pdal ground
    cmd="time pdal ground -i $FNAME -o ${FNAME%.las*}_pg_s$2_c$3.las --slope $2 --cellSize $3 --classify"; # --writers.las.format=0";
    echo $cmd
    eval $cmd
done
