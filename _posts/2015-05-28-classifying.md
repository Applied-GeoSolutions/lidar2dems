---
layout: page
title: "Classifying"
category: tut
date: 2015-06-01 07:55:24
order: 1
---

The first step in processing new LiDAR data is to create a site shapefile for the region that DEMs are desired.  Since it is important that the site polygon(s) cover data regions, a point density image of the data can be used to create the site shapfile.  Generate a point density image:

	$ l2d_dems density las/

where *las/* is the location containing the las files.  This will create a density.den.tif file in the current directory containing the point density for all available data.  A density image is shown below, and polygons have been drawn to completely cover all the data, although this is not necessary. The region of interest may just be a piece, or pieces of all the available data.

![point density image and site shapefile](/lidar2dems/assets/site-1.png)

The created shapefile should use the same SRS as the LiDAR data.  Additionally, an attribute has been added to the shapefile. For each drawn polygon, the terrain type is determined (1-4, as described on the [Concepts](concepts) page). The attribute table is shown below for the 19 features in the shapefile shown above.

![attribute table of site shapefile](/lidar2dems/assets/site-2.png)

Now with the site shapefile in hand, the LiDAR can be classified according to terrain type.  Call the l2d_classify utility with the shapefile:

	$ l2d_classify las/ -s site.shp --outdir lasclass

This will create classified las files in the lasclass/ directory, one file for each polygon in the site file, as shown below:

~~~
$ ls lasclass/
features-0_l2d_s1c3.las   features-13_l2d_s1c3.las  features-17_l2d_s1c2.las  features-3_l2d_s1c3.las  features-7_l2d_s1c2.las
features-10_l2d_s1c2.las  features-14_l2d_s1c2.las  features-18_l2d_s1c3.las  features-4_l2d_s1c3.las  features-7_l2d_s1c3.las
features-11_l2d_s1c2.las  features-15_l2d_s1c3.las  features-1_l2d_s1c3.las   features-5_l2d_s1c2.las  features-8_l2d_s1c3.las
features-12_l2d_s1c3.las  features-16_l2d_s1c2.las  features-2_l2d_s1c3.las   features-6_l2d_s1c2.las  features-9_l2d_s1c3.las
~~~

The lasclass/ directory will now be used as input to the l2d_dems function when creating DTMs and DSMs.
