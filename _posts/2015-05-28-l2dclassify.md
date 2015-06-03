---
layout: page
title: "l2d_classify"
category: doc
date: 2015-05-28 22:46:23
order: 2
---

The l2d_classify script is used to classify unclassified point clouds into ground and non-ground points. New las files will be output, and depending on the options provided, may be merged classified version of some or all the input las files.

~~~
$ l2d_classify -h
usage: l2d_classify [-h] [-s SITE] [--slope SLOPE] [--cellsize CELLSIZE]
                    [--outdir OUTDIR] [--decimation DECIMATION] [-v]
                    lasdir

Classify LAS file(s)

positional arguments:
  lasdir                Directory of LAS file(s) to classify

optional arguments:
  -h, --help            show this help message and exit
  -s SITE, --site SITE  Polygon(s) to process (default: None)
  --slope SLOPE         Slope (override) (default: None)
  --cellsize CELLSIZE   Cell Size (override) (default: None)
  --outdir OUTDIR       Output directory location (default: ./)
  --decimation DECIMATION
                        Decimate the points (steps between points, 1 is no
                        pruning (default: None)
  -v, --verbose         Print additional info (default: False)
~~~

A directory containing las files is required. It does not matter if the LAS files are already classified, lidar2dems will classify them, ignoring the existing classifications and output new files to the provided output directory (outdir), or the current directory if not provided.

If a site file is provided, there will be a single classified las file for each polygon. The file will have a name based on the site shapfile name, the Feature ID (FID) of the polygon, and the classification parameters used, as shown below for a site file called features.shp containing 19 polygons.

~~~
$ ls output_directory
features-0_l2d_s1c3.las   features-13_l2d_s1c3.las  features-17_l2d_s1c2.las  features-3_l2d_s1c3.las  features-7_l2d_s1c2.las
features-10_l2d_s1c2.las  features-14_l2d_s1c2.las  features-18_l2d_s1c3.las  features-4_l2d_s1c3.las  features-7_l2d_s1c3.las
features-11_l2d_s1c2.las  features-15_l2d_s1c3.las  features-1_l2d_s1c3.las   features-5_l2d_s1c2.las  features-8_l2d_s1c3.las
features-12_l2d_s1c3.las  features-16_l2d_s1c2.las  features-2_l2d_s1c3.las   features-6_l2d_s1c2.las  features-9_l2d_s1c3.las
~~~

The classification process is the most time consuming of the entire lidar2dems workflow.  Optional filters may be used to help speed up classification but should be used with caution because of trade-offs between processing time and product quality. For example, decimation will reduce processing time, but will prune the total number of points as discussed in [Concepts](concepts), which may or may not result in acceptable DEM products.

If a site file is not provided, all of the tiles will be merged together, classified, and output as a single las file. 

If a site file is not provided, or the site file does not contain the 'class' attribute, the classification parameters used will be 1 for the slope and 3 for the cellsize


