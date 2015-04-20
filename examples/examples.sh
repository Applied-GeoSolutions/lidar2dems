#!/bin/bash

# example commands

# create vrt of photos
#gdalbuildvrt photos_lowres.vrt lowres_photos/*.tif

# warp a bunch of p2g output files and crop to some bounds
for f in dems/*.tif; do ft=${f%.*}; gdalwarp $f ${ft%.*}_grid.${ft##*.}.tif -te 211980.0 9751933.0 235745.0 9754300.0 -r bilinear; done

# classify LAS files if they haven't been done yet
for d in Polygon_*; do if [ ! -d $d/Classified_LAS ]; then mkdir $d/Classified_LAS; echo $d; l2d_classify $d/LAS/*.las --outdir $d/Classified_LAS; fi; done