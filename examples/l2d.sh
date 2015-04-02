#!/bin/bash

# suggested workflow assumes there is a LAS directory with original las files. 
# Output will be created in subdirectories in current directory
# Example:
# $ l2d.sh 32750 211980.0 9751933.0 235745.0 9754300.0

# get bounds and EPSG for this polygon
EPSG=$1

# run classify on original files
l2d_classify LAS/*0.las -s 1 -c 3 --outdir Classified_LAS

# create dems
l2d_createdems Classified_LAS/*c3.las --dsm 0.56419 --dtm 0.56419 1.0 1.4142 2.0 2.5 3.0 --bounds $2 $3 $4 $5 --epsg $EPSG --outdir DEMs

# create vrt of photos
gdalbuildvrt photos_lowres.vrt lowres_photos/*.tif
