---
layout: page
title: "Creating a DTM"
category: tut
date: 2015-05-28 22:38:48
order: 4
---

With a directory of classified las files, a DTM can now be generated.  A DTM represents the ground elevation and can be caculated a few different ways, all of which are output. In heavily forested areas where the ground is obscured there can be relatively few ground points and gappy DTMs can result. In these cases the DTM can be gridded using progressively larger search radii, then gap-filled as described on the [Concepts](doc/concepts) page. In the example below, points collect at an angle off nadir greater than 20 degrees are filtered out.

        $ l2d_dems dtm lasclass/ -s features.shp --outdir dems --maxangle 20 --gapfill --radius 0.56 1.41 2.50 3.00

This will create a set of DTM files, one for each polygon in the site file, containing all the DTM products: density (.den.tif), minimum ground (.min.tif), maximum ground (.max.tif), and a mean using inverse distance weighted method (.idw.tif). A separate set of files will be created for each provided search radius. The listing below only shows the first of the 20 features for terseness, but the directory contains another set for each polygon.

~~~
$ ls dems/features-0*dtm*r*
features-0_dtm_r0.56.den.tif  features-0_dtm_r1.41.den.tif  features-0_dtm_r2.50.den.tif  features-0_dtm_r3.00.den.tif
features-0_dtm_r0.56.idw.tif  features-0_dtm_r1.41.idw.tif  features-0_dtm_r2.50.idw.tif  features-0_dtm_r3.00.idw.tif
features-0_dtm_r0.56.max.tif  features-0_dtm_r1.41.max.tif  features-0_dtm_r2.50.max.tif  features-0_dtm_r3.00.max.tif
features-0_dtm_r0.56.min.tif  features-0_dtm_r1.41.min.tif  features-0_dtm_r2.50.min.tif  features-0_dtm_r3.00.min.tif
~~~

Looking at the 5th polygon (features-4), it can be seen how increasing the radius fills the gaps.

####radius = 0.56
![DTM with radius 0.56](/lidar2dems/assets/dtm-1.png)

####radius = 1.41
![DTM with radius 1.41](/lidar2dems/assets/dtm-2.png)

####radius = 2.50
![DTM with radius 2.50](/lidar2dems/assets/dtm-3.png)

####radius = 3.00 
![DTM with radius 3.00](/lidar2dems/assets/dtm-4.png)

Because the --gapfill switch was provided, the different radius versions are used to gapfill (followed by nearest neighbor).  Below is the image for the 5th polygon, which has also been clipped to the actual area of the polygon (the images above include points in tiles that were included, but fell outside the polygon). 

####Gap-filled
![Gap-filled DTM](/lidar2dems/assets/dtm-5.png)

~~~
$ ls dems/features*dtm.*.tif
features-0_dtm.idw.tif   features-13_dtm.idw.tif  features-17_dtm.idw.tif  features-3_dtm.idw.tif  features-7_dtm.idw.tif
features-0_dtm.max.tif   features-13_dtm.max.tif  features-17_dtm.max.tif  features-3_dtm.max.tif  features-7_dtm.max.tif
features-0_dtm.min.tif   features-13_dtm.min.tif  features-17_dtm.min.tif  features-3_dtm.min.tif  features-7_dtm.min.tif
features-10_dtm.idw.tif  features-14_dtm.idw.tif  features-18_dtm.idw.tif  features-4_dtm.idw.tif  features-8_dtm.idw.tif
features-10_dtm.max.tif  features-14_dtm.max.tif  features-18_dtm.max.tif  features-4_dtm.max.tif  features-8_dtm.max.tif
features-10_dtm.min.tif  features-14_dtm.min.tif  features-18_dtm.min.tif  features-4_dtm.min.tif  features-8_dtm.min.tif
features-11_dtm.idw.tif  features-15_dtm.idw.tif  features-1_dtm.idw.tif   features-5_dtm.idw.tif  features-9_dtm.idw.tif
features-11_dtm.max.tif  features-15_dtm.max.tif  features-1_dtm.max.tif   features-5_dtm.max.tif  features-9_dtm.max.tif
features-11_dtm.min.tif  features-15_dtm.min.tif  features-1_dtm.min.tif   features-5_dtm.min.tif  features-9_dtm.min.tif
features-12_dtm.idw.tif  features-16_dtm.idw.tif  features-2_dtm.idw.tif   features-6_dtm.idw.tif
features-12_dtm.max.tif  features-16_dtm.max.tif  features-2_dtm.max.tif   features-6_dtm.max.tif
features-12_dtm.min.tif  features-16_dtm.min.tif  features-2_dtm.min.tif   features-6_dtm.min.tif
~~~

Finally, l2d_dems creates a merged VRT file using all of the individual polygons for both the maximum and the density products, which can then be viewed in QGIS or any other GIS program that supports GDAL file formats. The min and max versions look identical to idw within a screenshot, as the differences are very slight.

~~~
$ ls dems/dtm*
dtm.den.vrt  dtm.idw.vrt  dtm.max.vrt  dtm.min.vrt
~~~

####Density image
![point density of DSM](/lidar2dems/assets/dtm-6.png)

####DTM (idw) image
![DTM (idw) image](/lidar2dems/assets/dtm-7.png)


