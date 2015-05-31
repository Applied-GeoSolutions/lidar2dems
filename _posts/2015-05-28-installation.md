---
layout: page
title: "Installation"
category: doc
date: 2015-05-28 21:00:45
order: 0
---

The installation of lidar2dems itself is straightforward, as it only consists of a Python library and some scripts. However, there are several required dependencies that need a more manual process. These installation notes are for Ubuntu 14.04, but should work for most debian-based linux systems.

An easy-install.sh script is available in the repository.   Download it from here and run it in a temporary working directory (it can be deleted afterward).  If the easy install process is sucessful, you can disregard the rest of these installation notes.

## Installing Dependencies
Some of the dependencies can be easily installed via the Ubuntu packaging tool (apt), while others aren't available in such form and must be compiled from the source code.

### Dependencies from packages
Some dependencies are available via repositories, or the Ubuntu GIS repository.

~~~~
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get install git cmake g++ libboost-all-dev libgdal1-dev libeigen3-dev libflann-dev libopenni-dev libvtk5.8-qt4 libqhull-dev qt-sdk libvtk5-qt4-dev libpcap-dev python-vtk libvtk-java python-numpy libgeotiff-dev
~~~~

### Dependencies from source
These are dependencies that must be built from source code, and are available on GitHub.

**Running CMake**: Several of the programs below use cmake which works in a standard fashion across platforms. The best approach is to create an out-of-source build, meaning that a build directory is created somewhere other than the source directory. Follow the steps below for any source that utilizes cmake for building.

~~~
$ cd "projdir"      # "projdir" is the project directory
$ mkdir build
$ cd build
$ cmake -G "Unix Makefiles" ../
$ make
$ sudo make install
~~~


#### LASzip
LASzip is used by many other LiDAR software packages to support compressed LAS files. It is not needed if you are using LAS files, however since it installs easily it is best to install now, so that PDAL can be built with LASzip support.

1. Clone repository

        $ git clone https://github.com/LASzip/LASzip.git

2. Run CMake steps as above

#### Points2Grid
Points2Grid is used by PDAL to create rasters from point clouds using a local gridding method. It will not be used directly, but is used by PDAL.

1. Clone repository

    $ git clone git@github.com:CRREL/points2grid.git

2. Run CMake steps as above

###Installation:
1. Install PCL with the provided script

        $ scripts/pcl.sh


#### PDAL
PDAL is library for conversion and filtering of LiDAR data. It is under very active development and has features particularly well suited to batch processing.  It can also incorporate PCL for doing advanced algorithms on point clouds.

PDAL Documentation: http://www.pdal.io/docs.html

1. Clone repository

        $ git clone git@github.com:PDAL/PDAL.git pdal

2. Run CMake as above except use these parameters. On nonstandard systems, or other operating systems, the paths to some of the libraries may need to be modified.
        
        $ cmake -G "Unix Makefiles" ../ -DBUILD_PLUGIN_PCL=ON -DPCL_DIR=/usr/share/pcl-1.7 -DBUILD_PLUGIN_P2G=ON -DBUILD_PLUGIN_PYTHON=ON -DLASZIP_INCLUDE_DIR=/usr/local/include

