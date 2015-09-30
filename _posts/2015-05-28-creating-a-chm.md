---
layout: page
title: "Creating a CHM"
category: tut
date: 2015-05-28 22:38:58
order: 5
---

With final gap-filled versions of the DTM and DSM, a CHM can be generated. 

	$ l2d_chm dems/dsm.max.vrt dems/dtm.idw.vrt --fout dems/CHM.tif --hillshade

This uses the previously created, complete DSM and DTM images to create a CHM.tif image in the dems directory.  The hillshade switch also creates a CHM-hillshade.tif file using the 'gdaldem hillshade' utility.

If a shapefile is provided then the CHM will be calculated for each of the features in the shapefile (provided the DSM and DTM were created the same way). The DSM and DTM for each feature will be used to calculate the CHM, then all the output files merged into a VRT file.  In the example below for each feature the features-X_dsm.max.tif and features-X_dtm.idw.tif will be found for each feature (where feature is X).

	$ l2d_chm dems -s features.shp --hillshade

Which results in the files shown:

~~~
$ ls dems/*chm*
chm_hillshade.tif  features1-0_chm_hillshade.tif  features1-1_chm_hillshade.tif  features1-2_chm_hillshade.tif  features1-3_chm_hillshade.tif
chm.vrt            features1-0_chm.tif            features1-1_chm.tif            features1-2_chm.tif            features1-3_chm.tif
~~~

####CHM image
![Canopy Height Model](/lidar2dems/assets/chm-1.png)

####CHM hillshade image
![Canopy Height Model Hillshade](/lidar2dems/assets/chm-2.png)
