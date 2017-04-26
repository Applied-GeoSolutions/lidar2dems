#!/bin/bash

L2D_CHECKOUT=master
LASZIP_CHECKOUT=tags/2.0.2
PCL_CHECKOUT=tags/pcl-1.7.2
GIPPY_VERSION=0.3.9

DISTRO=$(lsb_release -is)
RELEASE=$(lsb_release -rs)
NUMTHREADS=2
# if [[ -f /sys/devices/system/cpu/online ]]; then
# 	# Calculates 1.5 times physical threads
# 	NUMTHREADS=$(( ( $(cut -f 2 -d '-' /sys/devices/system/cpu/online) + 1 ) * 15 / 10  ))
# fi

function install_system_dependencies() {
    SWIG_DEPS=swig2.0
    if [ "${DISTRO}" != "Ubuntu" ] ; then
        echo "Hasn't been tested with non-ubuntu distributions (${DISTRO})" >&2
        exit -1
    elif [ "${RELEASE}" = "14.04" ] ; then
        SWIG_DEPS="${SWIG_DEPS} swig"
    elif [ "${RELEASE}" != "16.04" ] ; then
        echo "Hasn't been tested with Ubuntu ${RELEASE}." >&2
        echo """If you take the time to make lidar2dems work 
with another Ubuntu release or distro, please
consider posting your script back to an issue on 
github <https://github.com/Applied-GeoSolutions/lidar2dems/issues/new?title=support for ${DISTRO}-${RELEASE}&body=attached is an updated easy-install.sh script>.
    """ >&2
        exit -2
    fi

    GIPPY_SYS_DEPS="${SWIG_DEPS}
                    python g++ libboost-all-dev libgdal-dev libgdal-dev
                    gdal-bin python-pip python-numpy python-scipy python-gdal"
    L2D_STACK_DEPS="${GIPPY_SYS_DEPS}
                    cmake++ libeigen3-dev libflann-dev libopenni-dev libqhull-dev
                    qt-sdk libvtk5-qt4-dev libpcap-dev python-vtk libvtk-java
                    libgeotiff-dev python-setuptools libxslt1-dev python-wheel
                    libgeos++-dev libxslt-dev"

    echo Installing dependencies
    apt-get update
    apt-get install -y ${L2D_STACK_DEPS}
}

function install_laszip() {
    echo checking for laszip
    LASZIP_CONFIG=$(which laszip-config)
    if [ ! "${LASZIP_CONFIG}" ] ;
    then
        echo Installing LASzip
        git clone https://github.com/LASzip/LASzip.git
        cd LASzip
        git checkout ${LASZIP_CHECKOUT}
        mkdir build
        cd build
        cmake -G "Unix Makefiles" ../
        make
        make install
        cd ../..
    else
        echo "LASzip already installed (${LASZIP_VERSION})."
    fi
}

function install_points2grid() {
    echo checking for points2grid
    P2G=$(which points2grid)
    if [ ! "${P2G}" ] ;
    then
        echo Installing Points2Grid
        git clone https://github.com/CRREL/points2grid.git
        cd points2grid
        mkdir build
        cd build
        cmake -G "Unix Makefiles" ../
        make
        make install
        cd ../..
    else
        echo "points2grid already installed."
    fi
}

function install_pcl() {
    echo checking for PCL
    PCL=$(which pcl_ply2ply)
    if [ ! "${PCL}" ] ;
    then
        echo Installing PCL
        git clone https://github.com/PointCloudLibrary/pcl.git
        cd pcl
        mkdir build
        cd build
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
        make install
        cd ../..
    else
        echo "PCL already installed (${PCL} exists)."
    fi
}

function install_pdal() {
    echo checking for PDAL
    PDAL_CONFIG=$(which pdal-config)
    if [ ! "${PDAL_CONFIG}" ] ;
    then
        # install PDAL
        wget https://github.com/PDAL/PDAL/archive/1.0.1.tar.gz
        tar -xzf 1.0.1.tar.gz
        cd PDAL-1.0.1;
        mkdir build
        cd build;
        cmake -G "Unix Makefiles" ../ -DBUILD_PLUGIN_PCL=ON -DBUILD_PLUGIN_P2G=ON -DBUILD_PLUGIN_PYTHON=ON -DPDAL_HAVE_GEOS=YES
        make;
        make install;
        cd ../..
    else
        echo "PDAL already installed (${PDAL_VERSION})."
    fi
}


function install_gippy() {
    echo checking for gippy
    # install gippy
    INSTALLED_VERSION=$(pip freeze | grep gippy | sed 's/gippy==//')
    if [ "${GIPPY_VERSION}" != "${INSTALLED_VERSION}" ] ;
    then
        pip install https://github.com/Applied-GeoSolutions/gippy/archive/v${GIPPY_VERSION}.tar.gz
    else
        echo "GIPpy already installed (${GIPPY_VERSION})."
    fi
}

function install_lidar2dems() {
    echo installing lidar2dems
    # install lidar2dems
    if [ -e lidar2dems ] ; then
        rm -rf lidar2dems
    fi

    # IF YOU ARE RUNNING THIS, WE ASSUME YOU'RE REINSTALLING.
    if [ "$(pip freeze | grep lidar2dems)" ] ; then
        pip uninstall -y lidar2dems
    fi
    git clone https://github.com/Applied-GeoSolutions/lidar2dems
    cd lidar2dems
    git checkout ${L2D_CHECKOUT}
    git pull
    ./setup.py install
    cd ..
}

function test_lidar2dems() {
    # run tests
    pip install nose
    cd lidar2dems ; time nosetests --with-xunit test
}


if [ $0 != "bash" ] ; then
    cd /usr/local/src/
    install_system_dependencies
    install_laszip
    install_points2grid
    install_pcl
    install_pdal
    install_gippy
    install_lidar2dems
    test_lidar2dems
else
    echo """
    Adding functions to your environment for
    manually installing lidar2dems components:

        install_system_dependencies
        install_laszip
        install_points2grid
        install_pcl
        install_pdal
        install_gippy
        install_lidar2dems
        test_lidar2dems

   *** 
       Note: each function depends on the previous functions running, or the
       associated software being installed by another means.
   ***

"""
fi

