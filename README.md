# LiDAR tools

This project is a collection of information and possibly source code for LiDAR utilities. The installation notes here are for Ubuntu 14.04.  Most of the open-source LiDAR tools available are not available as pre-built packages and must be compiled from source.  Start in a working build directory (e.g., ~/build). The instructions for each package assume you start in this working directory.

# Installation Notes
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

# Recommended LiDAR Software
## LASzip:
LASzip is used by many other LiDAR software packages to support compressed LAS files.
1. Clone repository
2. *Run CMake steps as above*
> `$ git clone https://github.com/LASzip/LASzip.git`

## PDAL
PDAL has excellent documentation:
> Main Documentation: http://www.pdal.io/docs.html
> Installation: http://www.pdal.io/compilation/unix.html
1. Clone repository
> `$ git clone git@github.com:PDAL/PDAL.git pdal`
2. Run CMake as above
> If there is an error when calling cmake about not finding LASzip.hpp specify the include directory when calling cmake:
> `$ cmake -G "Unix Makefiles" -DLASZIP_INCLUDE_DIR=/usr/local/include`

In order to use the PCL pipeline within PDAL, including visualization, a separate branch of PCL must be installed.  
1. Make sure the normal PCL distribution is removed from your system
> `sudo apt-get purge libpcl-all`
2. Install dependencies
> `sudo apt-get install libeigen3-dev libflann-dev libopenni-dev libvtk5.8-qt4 libqhull-dev qt-sdk libvtk5-qt4-dev libpcap-dev`
3. Clone repository
> `$ git clone https://github.com/chambbj/pcl.git`
> `$ cd pcl`
> `$ git checkout pipeline`
4. Run CMake as above


## MCC-LiDAR
MCC-LiDAR consists of a command line utility for performing classification using the MCC algorithm, which is particularly well suited for classifying ground points amidst canopy cover. MCC is the classification algorithm endorsed by the Forest Service

# Other LiDAR Software
There are some other LiDAR libraries which may have promise, but not widely used 

## Fusion
Fusion is a Windows only GUI program that supports visualization and classification using the MCC algorithm. Because of the GUI nature it is not particularly well suited to batch processing. It also requires conversion of .las files to an image prior to loading of the .las file (which must be done to do classification). These extra steps also make the entire process slower.

## libLAS:
Depends on LASzip
1. Clone repository
    > `$ git clone https://github.com/libLAS/libLAS.git`
2. Run CMake steps as above
    

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
### Installation
    http://idav.ucdavis.edu/~okreylos/ResDev/LiDAR/
    1. Install dependencies
        $ sudo apt-get install ndvidia-current
    2. Download and run Ubuntu install script for Vrui: http://idav.ucdavis.edu/~okreylos/ResDev/Vrui/Download.html
        Script creates two folders ~/src/Vrui-X.X and ~/Vrui-X.X
    3. Download and untar LidarViewer: http://idav.ucdavis.edu/~okreylos/ResDev/LiDAR/ 
        Follow instructions in README
        Recommend following optional steps 4 and 6 to edit makefile: change INSTALLDIR to /usr/local
    4. Online docs at http://wiki.cse.ucdavis.edu/keckcaves:lidarmanual
### Use
    1. Convert files to LIDAR format (.lidar)
        $ LidarPreprocessor fname.las -LIDAR -o fname
    2. Visualize
        $ LidarViewer fname.lidar
