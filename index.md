---
layout: default
title: "lidar2dems"
---

#lidar2dems 
The [lidar2dems](http://github.com/Applied-GeoSolutions/lidar2dems) project is a collection open-source (FreeBSD license) command line utilities for supporting the easy creation of Digital Elevation Models (DEMs) from LiDAR data. lidar2dems uses the PDAL library (and associated dependencies) for doing the actual point processing and gridding of point clouds into raster data.

A Digital Elevation Model (DEM) is the generic name for any raster data containing elevation data. There are 3 types of DEMs that lidar2dems can generate:

* Digital Terrain Model (DTM) - This is the calculated elevation using only points classified as ground.
* Digtial Surface Model (DSM) - This is the calculated elevation using the highest non-ground points. In forested areas this corresponds to the absolute elevation of the top of the canopy, but it could also be the roofs of buildings or other structures.
* Canopy Height Model (CHM) - This is the difference between the DSM and DTM, which is presumed to be a forested area, thus 'Canopy Height'.

Currently only LAS LiDAR files are supported. However, lidar2dems can handle any number of input point clouds for a given region of interest, be they tiles, swaths, or any arbitrary footprint. A region of interest is defined by a shapefile, called a 'site' file, which must also be in the same reference system as the LAS file(s). Points can be filters with a variety of options, and resulting DEMs can be gap-filled.

####Utilities

* l2d_classify - classify points (into ground and non-ground) in a collection of LAS files
* l2d_dems - generate images of point density, a Digital Terrain Model (DTM), or a Digital Surface Model (DSM)
* l2d_chm - generate image of a Canopy Height Model (CHM) given a DTM and DSM 

####Funding

lidar2dems was created by [Applied GeoSolutions, LLC](http://www.appliedgeosolutions.com) and the University of New Hampshire as part of a NASA-funded Carbon Monitoring System Project (NASA grant #NNX13AP88G; PI Stephen Hagen). In this project, Applied GeoSolutions and project partners are working with the government of Indonesia to improve forest monitoring in Kalimantan by composing detailed, high resolution maps of forest carbon. If you have questions about this project please email [oss@appliedgeosolutions.com](mailto:oss@appliedgeosolutions.com)

####Authors and Contributors

* [Matthew Hanson](http://github.com/matthewhanson), matt.a.hanson@gmail.com
* Frankie Sullivan, franklin.sullivan@unh.edu
* Steve Hagen, shagen@appliedgeosolutions.com
* Ian Cooke, icooke@appliedgeosolutions.com

See the [lidar2dems GitHub page](http://github.com/Applied-GeoSolutions/lidar2dems) for the source and issue tracker.

