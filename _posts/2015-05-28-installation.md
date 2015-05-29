---
layout: page
title: "Installation"
category: doc
date: 2015-05-28 21:00:45
order: 0
---

The installation of lidar2dems itself is straightforward as it is a set of Python-based command line tools. However, there are several required dependencies that need a more manual process. These installation notes are for Ubuntu 14.04, but should work for most debian-based linux systems.

## Installation Notes

### Initial Dependencies
Many of the dependencies are geospatial libraries and projects that are available in the Ubuntu GIS repository.

~~~~
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get install git cmake libboost-all-dev libgdal1-dev
~~~~

## Running CMake
Many of the programs use cmake which works in a standard fashion across platforms. The best approach is to create an out-of-source build, meaning that a build directory is created somewhere other than the source directory
```
$ cd "projdir"      # "projdir" is the project directory
$ mkdir build
$ cd build
$ cmake -G "Unix Makefiles" ../
$ make
$ sudo make install
```

# Installing from Source

## LASzip
LASzip is used by many other LiDAR software packages to support compressed LAS files.

1. Clone repository

        $ git clone https://github.com/LASzip/LASzip.git

2. Run CMake steps as above

## Points2Grid
Points2Grid is used by PDAL to create DEM products from point clouds using a local gridding method

1. Clone repository

    $ git clone git@github.com:CRREL/points2grid.git

2. Run CMake steps as above


## PDAL
PDAL is the newest LiDAR library for conversion and filtering. It is under very active development and has features particularly well suited to batch processing. There is also excellent documentation: http://www.pdal.io/docs.html

        $ sudo apt-get install libeigen3-dev libflann-dev libopenni-dev libvtk5.8-qt4 libqhull-dev qt-sdk libvtk5-qt4-dev libpcap-dev python-vtk libvtk-java python-numpy libgeotiff-dev

###Installation:
1. Install PCL with the provided script

        $ scripts/pcl.sh

2. Clone repository

        $ git clone git@github.com:PDAL/PDAL.git pdal

3. Run CMake as above except when running "cmake" give these parameters (the LASZIP may not be necessary but for some reason it was not found on test systems):
        
        $ cmake -G "Unix Makefiles" ../ -DBUILD_PLUGIN_PCL=ON -DPCL_DIR=/usr/share/pcl-1.7 -DBUILD_PLUGIN_P2G=ON -DBUILD_PLUGIN_PYTHON=ON -DLASZIP_INCLUDE_DIR=/usr/local/include
