# Installation of LiDAR tools on Ubuntu 14.04
======

Most of the open-source LiDAR tools available are not available as pre-built packages and must be compiled from source.  Start in a working build directory (e.g., ~/build). The instructions for each package assume you start in this working directory.

## Dependencies
These are dependencies that are used by many of the programs. Some will have unique dependencies which are specified in the actual package instructions below
~~~~
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get install git cmake libboost-all-dev libgdal0-dev
~~~~

## Running CMake
Many of the programs use cmake which works in a standard fashion across platforms. The best approach is to create an out-of-source build, meaning that a build directory is created somewhere other than the source directory
~~~~
$ cd "projdir"      # "projdir" is the project directory
$ mkdir build
$ cd build
$ cmake -G "Unix Makefiles" ../
$ make
$ sudo make install
~~~~

## PDAL



## LASzip:
1. Clone repository
> `$ git clone https://github.com/LASzip/LASzip.git`
2. Run CMake steps as above


## libLAS:
Depends on LASzip
1. Clone repository
> `$ git clone https://github.com/libLAS/libLAS.git`
2. Run CMake steps as above
    

## SPDLib:
### Installing from conda
    # Download miniconda and follow installation from here: http://conda.pydata.org/miniconda.html
    $ sudo conda install -c spdlib  spd3dpointsviewer tuiview
    # Install to system location '/usr/local/' rather than default
    # Answer 'yes' to add to path

### Installing from source
Requires LASzip and libLA
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

## SPDPointsViewer
    1)
    $ hg clone https://bitbucket.org/petebunting/spd-3d-points-viewer spdpointsviewer
    $ cd spdpointsviewer
    $ in CMakeLists.txt make the following changes:
        change GDAL_INCLUDE_DIR from /usr/local/include to /usr/include/gdal
    # Run CMake steps



## LiDAR Viewer
### Installation
    http://idav.ucdavis.edu/~okreylos/ResDev/LiDAR/
    1) Download and run Ubuntu install script for Vrui: http://idav.ucdavis.edu/~okreylos/ResDev/Vrui/Download.html
        Script creates two folders ~/src/Vrui-X.X and ~/Vrui-X.X
    2) Download and untar LidarViewer: http://idav.ucdavis.edu/~okreylos/ResDev/LiDAR/ 
        Follow instructions in README
        Recommend following optional steps 4 and 6 to edit makefile: change INSTALLDIR to /usr/local
    3) Online docs at http://wiki.cse.ucdavis.edu/keckcaves:lidarmanual
### Use
    1) Convert files to LIDAR format (.lidar)
        $ LidarPreprocessor fname.las -LIDAR -o fname
    2) Visualize
        $ LidarViewer fname.lidar
