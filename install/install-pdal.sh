#!/usr/bin/env bash

# Install LASzip
git clone https://github.com/LASzip/LASzip.git
cd LASzip
mkdir build
cd build
cmake -G "Unix Makefiles" ../
make
sudo make install

# Install PCL
sudo apt-get purge libpcl-all
sudo apt-get install libeigen3-dev libflann-dev libopenni-dev libvtk5.8-qt4 libqhull-dev qt-sdk libvtk5-qt4-dev libpcap-dev
git clone https://github.com/chambbj/pcl.git
cd pcl
git checkout pipeline
mkdir build
cd build
cmake -G "Unix Makefiles" ../
make
sudo make install

# Install PDAL
git clone git@github.com:PDAL/PDAL.git pdal
cd pdal
mkdir build
cd build
cmake -G "Unix Makefiles" ../ -DBUILD_PLUGIN_PCL=ON
