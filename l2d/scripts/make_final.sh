#!/bin/bash -x

# create final, clipped products

BOUNDS="212000 9751900 235800 9754300"
RES="1.0 1.0"
INTERP=bilinear
OUTDIR=final
ARGS="-srcnodata -9999 -dstnodata -9999"

# DSM
gdalwarp DSM_r0.56419.max.vrt $OUTDIR/DSM.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS

# Photos
gdalwarp photos_lowres.vrt $OUTDIR/photos_lowres.tif -te $BOUNDS -tr 0.5 0.5 -r $INTERP

# Point density (all points)
gdalwarp DSM_r0.56419.den.vrt $OUTDIR/PointDensity.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS

# DTMs
gdalwarp DTM_r0.56419.idw.vrt $OUTDIR/DTM_r0.5.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS
gdalwarp DTM_r1.idw.vrt $OUTDIR/DTM_r1.0.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS
gdalwarp DTM_r1.4142.idw.vrt $OUTDIR/DTM_r1.4.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS
gdalwarp DTM_r2.0.idw.vrt $OUTDIR/DTM_r2.0.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS
gdalwarp DTM_r2.5.idw.vrt $OUTDIR/DTM_r2.5.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS
gdalwarp DTM_r3.0.idw.vrt $OUTDIR/DTM_r3.0.tif -te $BOUNDS -tr $RES -r $INTERP $ARGS

# create hillshades
gdaldem hillshade $OUTDIR/DSM.tif $OUTDIR/DSM_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r0.5.tif $OUTDIR/DTM_r0.5_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r1.0.tif $OUTDIR/DTM_r1.0_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r1.4.tif $OUTDIR/DTM_r1.4_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r2.0.tif $OUTDIR/DTM_r2.0_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r2.5.tif $OUTDIR/DTM_r2.5_hillshade.tif
gdaldem hillshade $OUTDIR/DTM_r3.0.tif $OUTDIR/DTM_r3.0_hillshade.tif
