#!/bin/bash

# Arguments:  directory, slope, cellsize

FILENAMES=$1/*0.las

date
echo "File count = " `ls -1 $FILENAMES | wc -l`

for FNAME in $FILENAMES; do
    # run pdal ground
    FOUT=${FNAME%.las*}_pg_s$2_c$3.las
    if [ ! -f $FOUT ]; then
        cmd="time pdal ground -i $FNAME -o $FOUT --slope $2 --cellSize $3 --classify"; # --writers.las.format=0";
        echo $cmd
        eval $cmd
    fi
done
