#!/bin/bash
################################################################################
#   lidar2dems - utilties for creating DEMs from LiDAR data
#
#   AUTHOR: Matthew Hanson, matt.a.hanson@gmail.com
#
#   Copyright (C) 2015 Applied Geosolutions LLC, oss@appliedgeosolutions.com
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#   
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

# script to classify LAS files and generate complete set of density, DSM, DTM, and CHM products

d=$1

site=features.shp
bsite=${filename%.*}
lasdir=lasclass
demdir=dems

echo Creating DEMs for directory $d

echo Creating density image
l2d_dems density $d/LAS -s $d/$site --outdir $d/$demdir

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
