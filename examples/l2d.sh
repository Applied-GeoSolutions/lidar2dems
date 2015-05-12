#!/bin/bash

# script to classify LAS files and generate complete set of density, DSM, DTM, and CHM products

d=$1

site=features.shp
bsite=${filename%.*}
lasdir=lasclass
demdir=dems

echo Creating DEMs for directory $d

echo Creating density image
l2d_dems density $d/LAS -s $d/$site --outdir $d/$demdir -c

echo Classifying with decimation
l2d_classify $d/LAS -s $d/$site --outdir $d/$lasdir --deci 10 

echo Creating DSM
l2d_dems dsm $d/$lasdir -s $d/$site --outdir $d/$demdir --gapfill --maxsd 2.5 --maxangle 19 --maxz 400

echo Creating DTM
l2d_dems dtm $d/$lasdir -s $d/$site --outdir $d/$demdir --gapfill --radius 0.56 1.41 2.50 3.00 
    
echo Creating CHM
l2d $d/dsm.max.vrt $d/dtm.idw.vrt --fout $d/chm.tif

echo Generating hillshades
gdaldem hillshade $d/dsm.max.vrt $d/dsm-hillshade.max.tif
gdaldem hillshade $d/dtm.idw.vrt $d/dtm-hillshade.idw.tif
