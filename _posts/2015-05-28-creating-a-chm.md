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

####CHM
![Canopy Height Model](/lidar2dems/assets/chm-1.png)

####CHM Hillshade
![Canopy Height Model Hillshade](/lidar2dems/assets/chm-2.png)
