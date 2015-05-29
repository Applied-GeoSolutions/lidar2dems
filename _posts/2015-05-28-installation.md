---
layout: page
title: "Installation"
category: docs
date: 2015-05-28 21:00:45
---


# LiDAR Tools Installation Notes
## Dependencies
These are dependencies that are used by many of the programs. Some will have unique dependencies which are specified in the actual package instructions below
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

# Recommended LiDAR Software

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


## libLAS:
libLAS is an older library, which is to eventually be replaced with PDAL. However, some other software (e.g., MCC-LiDAR) depends on libLAS. 

1. Install LASzip

2. Clone repository

        $ git clone https://github.com/libLAS/libLAS.git

3. Run CMake steps as above


## MCC-LiDAR
MCC-LiDAR consists of a command line utility for performing classification using the MCC algorithm, which is particularly well suited for classifying ground points amidst canopy cover. It does not classify the type of vegetation (e.g., low, medium, high), but this may be added in the future.

1. Clone repository

        $ svn checkout svn://svn.code.sf.net/p/mcclidar/code/trunk mcclidar-code

2. Run CMake steps as above

### Using MCC-LiDAR
Note that MCC-LiDAR is designed to replace all the classification codes in the input file.  It also requires setting some initial parameters, for which the guidelines can be used below as a starting point. For more detail on picking parameters see http://sourceforge.net/p/mcclidar/wiki/HowToRun/

Scale (S): Find the average point density, pd, for all returns for your dataset. Calculate S, then vary up and down in 0.1 increments to find best results.

            S = sqrt(1/pd)

Curvature (C): Start with a curvature of 0.3 if the terrain is relatively flat, and increase for more varying terrain.

On a test file of about 1 million points (~20MB), MCC-LiDAR took approximately 17 minutes to complete. If this were to scale linearly this is about 14.5 hours/GB or 618 days/TB.  MCC-LiDAR does not utilize multiple processors.

# LAStools
LAStools is a series of open-source utilities for working with LAS files such as lasinfo and las2ogr. It is not necessary, but lasinfo provides some useful info, and it will testing some of the other utilities (e.g., conversion) for speed against PDA>

1. Clone and unzip repository

        $ wget http://www.cs.unc.edu/~isenburg/lastools/download/LAStools.zip
        $ unzip LAStools.zip

2. Compile 
    
        $ cd LAStools 
        $ make

3. Install
        # cd bin
        $ sudo cp las2las las2las-old las2ogr las2txt las2txt-old lasblock lasindex lasinfo lasinfo-old lasmerge lasprecision laszip laszip-config laszippertest /usr/local/bin/


# Other LiDAR Software
There are some other LiDAR libraries which may have promise, but not widely used 

## Fusion
Fusion is a Windows only GUI program that supports visualization and classification using the MCC algorithm. Because of the GUI nature it is not particularly well suited to batch processing. It also requires conversion of .las files to an image prior to loading of the .las file (which must be done to do classification). These extra steps also make the entire process slower.

    

## SPDLib:
SPDLib is apparently rich with features, including classification and visualization. However, it is also quite difficult to install properly, is not under active development and is not as widely used as PDAL/PCL.  The easiest method to to install from conda (a packaging and installer tool that also utilizes virtual environments). SPDPointsViewer is a company program for SPDLib for visualizaing point clouds. It can also be installed via conda.

### Installing from conda
    # Download miniconda and follow installation from here: http://conda.pydata.org/miniconda.html
    $ sudo conda install -c spdlib  spd3dpointsviewer tuiview
    # Install to system location '/usr/local/' rather than default
    # Answer 'yes' to add to path

### Installing from source
This is the start of compilation notes, however I could never get it finally running so they are incomplete.

Requirements: LASzip and libLAS

SPDLib:
    $ sudo apt-get install mercurial libgsl0-dev libcgal-dev
    $ hg clone https://bitbucket.org/petebunting/spdlib spdlib
    $ cd spdlib
    # in CMakeLists.txt make the following changes:
        change GDAL_INCLUDE_DIR from /usr/local/include to /usr/include/gdal

    # Update the runtime library path (spdlib puts libs in /usr/local/lib)
    # Add new file /etc/ld.so.conf.d/99local.conf with one line:
    /usr/local/lib
    # Then run ldconfig to update it
    $ ldconfig
SPDPointsViewer:
    $ hg clone https://bitbucket.org/petebunting/spd-3d-points-viewer spdpointsviewer
    $ cd spdpointsviewer
    $ in CMakeLists.txt make the following changes:
        change GDAL_INCLUDE_DIR from /usr/local/include to /usr/include/gdal
    # Run CMake steps

## LiDAR Viewer

See main page here: http://idav.ucdavis.edu/~okreylos/ResDev/LiDAR/ and documentation at http://wiki.cse.ucdavis.edu/keckcaves:lidarmanual

1. Install dependencies

        $ sudo apt-get install ndvidia-current
        # Download and run Ubuntu install script for Vrui (http://idav.ucdavis.edu/~okreylos/ResDev/Vrui/Download.html) 

The Vrui download sript  will create two folders ~/src/Vrui-X.X and ~/Vrui-X.X

2. Download and untar LidarViewer from above link and follow installation instructions in README

3. Recommend following optional steps 4 and 6 to edit makefile: change INSTALLDIR to /usr/local

### Using LiDAR Viewer
    1. Convert files to LIDAR format (.lidar)
        $ LidarPreprocessor fname.las -LIDAR -o fname
    2. Visualize
        $ LidarViewer fname.lidar
