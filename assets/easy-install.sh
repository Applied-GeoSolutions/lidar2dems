#!/bin/bash

echo Installing dependencies
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt-get install -y git cmake g++ libboost-all-dev libgdal1-dev libeigen3-dev libflann-dev libopenni-dev libvtk5.8-qt4 libqhull-dev qt-sdk libvtk5-qt4-dev libpcap-dev python-vtk libvtk-java python-numpy libgeotiff-dev python-setuptools swig swig2.0 python-gdal python-scipy libxslt1-dev python-pip python-wheel libgeos++-dev

echo Installing LASzip
git clone https://github.com/LASzip/LASzip.git
cd LASzip; mkdir build; cd build; cmake -G "Unix Makefiles" ../
make; sudo make install; cd ../..

echo Installing Points2Grid
git clone https://github.com/CRREL/points2grid.git
cd points2grid; mkdir build; cd build; cmake -G "Unix Makefiles" ../
make; sudo make install; cd ../..

echo Installing PCL
NUMTHREADS=2
if [[ -f /sys/devices/system/cpu/online ]]; then
	# Calculates 1.5 times physical threads
	NUMTHREADS=$(( ( $(cut -f 2 -d '-' /sys/devices/system/cpu/online) + 1 ) * 15 / 10  ))
fi
git clone https://github.com/PointCloudLibrary/pcl.git
cd pcl; mkdir build; cd build
git fetch origin --tags
git checkout tags/pcl-1.7.2
cmake .. \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DBUILD_outofcore:BOOL=OFF \
    -DWITH_QT:BOOL=ON \
    -DWITH_VTK:BOOL=ON \
    -DWITH_OPENNI:BOOL=OFF \
    -DWITH_CUDA:BOOL=OFF \
    -DWITH_LIBUSB:BOOL=OFF \
    -DBUILD_people:BOOL=OFF \
    -DBUILD_surface:BOOL=ON \
    -DBUILD_tools:BOOL=ON \
    -DBUILD_visualization:BOOL=ON \
    -DBUILD_sample_consensus:BOOL=ON \
    -DBUILD_tracking:BOOL=OFF \
    -DBUILD_stereo:BOOL=OFF \
    -DBUILD_keypoints:BOOL=OFF \
    -DBUILD_pipeline:BOOL=ON \
    -DCMAKE_CXX_FLAGS="-std=c++11" \
    -DBUILD_io:BOOL=ON \
    -DBUILD_octree:BOOL=ON \
    -DBUILD_segmentation:BOOL=ON \
    -DBUILD_search:BOOL=ON \
    -DBUILD_geometry:BOOL=ON \
    -DBUILD_filters:BOOL=ON \
    -DBUILD_features:BOOL=ON \
    -DBUILD_kdtree:BOOL=ON \
    -DBUILD_common:BOOL=ON \
    -DBUILD_ml:BOOL=ON
make -j $NUMTHREADS
sudo make install
cd ../..

# install PDAL
git clone https://github.com/PDAL/PDAL.git
cd PDAL; git checkout tags/1.0.1
mkdir build; cd build; 
cmake -G "Unix Makefiles" ../ -DBUILD_PLUGIN_PCL=ON -DBUILD_PLUGIN_P2G=ON -DBUILD_PLUGIN_PYTHON=ON -DPDAL_HAVE_GEOS=YES
make; sudo make install; cd ../..

# install lidar2dems
sudo pip install gippy
git clone https://github.com/Applied-GeoSolutions/lidar2dems
cd lidar2dems
sudo ./setup.py install; cd ..
