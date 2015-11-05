#!/usr/bin/env python
################################################################################
#   lidar2dems - utilties for creating DEMs from LiDAR data
#
#   AUTHOR: Franklin Sullivan, fsulliva@gmail.com
#
#   Copyright (C) 2015 Applied Geosolutions LLC, oss@appliedgeosolutions.com
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

# Library functions for creating voxel rasters from Lidar data

import os, numpy, math
import gippy
import glob
from datetime import datetime
from laspy import file


# text file management
def run_las2txt(fin, fout, verbose=False):
    """ Run las2txt """
    cmd = [
        'las2txt',
        '-i %s' % fin,
        '-o %s' % fout,
        '-parse %s' % 'xyzirncpt',
        '-sep %s' % 'komma',
    ]
    if verbose:
        cmd.append('-v1')
        print ' '.join(cmd)
    out = os.system(' '.join(cmd))
    if verbose:
        print out

def delete_txtfile(f):
    """ Delete tmp txt file """
    cmd = [
	'rm',
	f,
	]
    out = os.system(' '.join(cmd))

# point record scaling functions

def scale_x(las_file, point):
    """ Calculate scaled value of x for point record """
    _px = point.X
    scale = las_file.header.scale[0]
    offset = las_file.header.offset[0]
    return _px*scale+offset
    
def scale_y(las_file, point):
    """ Calculate scaled value of x for point record """
    _py = point.Y
    scale = las_file.header.scale[1]
    offset = las_file.header.offset[1]
    return _py*scale+offset

def scale_z(las_file, point):
    """ Calculate scaled value of x for point record """
    _pz = point.Z
    scale = las_file.header.scale[2]
    offset = las_file.header.offset[2]
    return _pz*scale+offset


# dtm value location tools

def coldex(x, xi, res):

    out = int((x-xi)/res)

    return out


def rowdex(y, yi, res):

    out = int((yi-y)/res)

    return out


def get_dtm_value(dtm, x, y, xi, yi, dtm_res, y_size, x_size):
    """ Retrieve ground elevation below lidar return """

    col = coldex(x, xi, dtm_res)
    if (col == x_size):
	col = int(x_size-1)
    row = rowdex(y, yi, dtm_res)
    if (row == y_size):
	row = int(y_size-1)

    zd = dtm[row][col]

    return zd

# generation of voxels

def create_voxels(filenames, voxtypes=['count','intensity'], demdir='.', site=None, outdir='', overwrite=False, verbose=False):

    """ Create voxels from LAS file """

    start = datetime.now()
    # filename based on feature number
    bname = '' if site is None else site.Basename() + '_'
    dtmname = '%sdtm.idw.vrt' %bname
    chmname = '%schm.tif' %bname
    bname = os.path.join(os.path.abspath(outdir), '%s' % (bname))
    ext = 'tif'

    # products (vox)
    products = voxtypes
    fouts = {o: bname + '%s.voxels.%s' % (o, ext) for o in products}
    print fouts
    prettyname = os.path.relpath(bname) + ' [%s]' % (' '.join(products))

    # run if any products missing (any extension version is ok, i.e. vrt or tif)
    run = False
    for f in fouts.values():
        if len(glob.glob(f[:-3] + '*')) == 0:
            run = True

    if run or overwrite:
	# find dtm and chm files and check if they exist
	dtmpath = os.path.join(demdir, dtmname)
	if not os.path.exists(dtmpath):
	    dtmname = '%sdtm.idw.tif' %('' if site is None else site.Basename() + '_')
	    dtmpath = os.path.join(demdir, dtmname)
	chmpath = os.path.join(demdir, chmname)
	if not os.path.exists(chmpath):
	    chmname = 'chm.tif'
	    chmpath = os.path.join(demdir, chmname)
	print dtmpath, chmpath
	paths = [dtmpath, chmpath]
    	exists = all([os.path.exists(f) for f in paths])
	# print paths
    	if not exists:
            print 'DTM and/or CHM do not exist: Check DEM directory (%s)!' % (demdir)
            exit(0)

        print 'Creating %s from %s files' % (prettyname, len(filenames))
	voxelize(filenames,voxtypes,site,dtmpath,chmpath,outdir)
    else:
	print 'Already created %s in %s' % (voxtypes, os.path.relpath(outdir))
        exit(0)

    # check if voxel files were created
    exists=True
    for f in fouts.values():
        if not os.path.exists(f):
            exists = False
        if not exists:
            raise Exception("Error creating voxels: %s" % ' '.join(fouts))

    print 'Completed %s in %s' % (prettyname, datetime.now() - start)
    return fouts


def voxelize(lasfiles, products=['count','intensity'], site=None, dtmpath='', chmpath='', outdir=''):

    # filename based on demtype, radius, and optional suffix
    bname = '' if site is None else site.Basename() + '_'
    bname = os.path.join(os.path.abspath(outdir), '%s' % (bname))

    # product output image names
    denout = bname + 'count.voxels.tif'
    intout = bname + 'intensity.voxels.tif'

    # read dtm and chm arrays
    dtm_img = gippy.GeoImage(dtmpath)
    print 'opened dtm'
    chm_img = gippy.GeoImage(chmpath)
    print 'opened chm'
    chm_arr = chm_img[0].Read()
    print 'read chm'
    dtm_arr = dtm_img[0].Read()
    print 'read dtm'

    dtm_y_shape, dtm_x_shape = dtm_arr.shape

    # chmMax is the number of bands that will be necessary to populate the output grids
    chmMax = numpy.int16(math.ceil(numpy.percentile(chm_arr,99.999))+1)
    print 'max canopy height is ', chmMax

    # get geo information from dtm image - unsure if this is needed
    srs = dtm_img.Projection()
    dtm_gt = dtm_img.Affine()
    dtm_minx, dtm_maxy = dtm_gt[0], dtm_gt[3]

    # loop through las file and populate multi-dimensional grid
    # create rhp and rhi, multi-dimensional output grids - rhp is density, rhi is intensity sum
    print 'creating output arrays'
    rhp = numpy.zeros((chmMax,dtm_y_shape,dtm_x_shape))
    rhi = numpy.zeros((chmMax,dtm_y_shape,dtm_x_shape))
    print 'created them!'
    bands,nrows,ncols = rhp.shape

    print "Populating Voxels"

    for lasfile in lasfiles:
        print "Iterating over points in files %s" %(lasfile)

        f = file.File(lasfile,mode='r')
        for p in f:
	    # print 'x,y,z: ', p.x, p.y, p.z
	    p.make_nice()
	    x = scale_x(f, p)
	    y = scale_y(f, p)
	    z = scale_z(f, p)
	    c = p.classification
	    i = p.intensity

	    col = coldex(x, dtm_minx, 1.0)
	    row = rowdex(y, dtm_maxy, 1.0)

	    if (0 <= col < dtm_x_shape) & (0 <= row < dtm_y_shape):

		zd = get_dtm_value(dtm_arr, x, y, dtm_minx, dtm_maxy, 1.0, dtm_y_shape, dtm_x_shape)

	        if (c == 2):

	            band = 0

 	        else:

	            band = int(math.ceil(z-zd))

	        if (0 <= band < bands):

	            rhp[band][row][col] += 1
	            rhi[band][row][col] += i

	    else:
		pass


    # output rhp and rhi images using gippy
    
    if 'count' in products:
	print 'Writing %s' %denout, 'fullest pixel has %i returns' %numpy.max(rhp)
	# numpy.save(denout,rhp)
    	den_img = gippy.GeoImage(denout,dtm_img,gippy.GDT_Int16,bands)
	for b in range(0,bands):
	    den_img[b].Write(rhp[b])

    if 'intensity' in products:
	print 'Writing %s' %intout
	# numpy.save(intout,rhi)
        int_img = gippy.GeoImage(intout,dtm_img,gippy.GDT_Int32,bands)
	for b in range(0,bands):
            int_img[b].Write(rhi[b])
    
    # print "Completed Voxel products for %s" %(bname)

# post-processing of voxels

def aggregate(dat, window):
    """ Sums cubic meter voxels into coarser sizes """
    dim = len(dat.shape)
    if dim==2:
        shp = (dat.shape[-2]/window, dat.shape[-1]/window)
        agg = numpy.zeros(shp, dtype=int)
        y = 0
        while y+window <= shp[0]:
            y_ = y*window
            x = 0
            while x+window <= shp[1]:
                x_ = x*window
                agg[y,x] = numpy.sum(dat[y_:y_+window,x_:x_+window])
                x+=1
            y+=1
    if dim==3:
        shp = (dat.shape[-3], dat.shape[-2]/window, dat.shape[-1]/window)
        agg = numpy.zeros(shp, dtype=int)
        for z in range(0,shp[-3]):
            y = 0
            while y+window <= shp[-2]:
                y_ = y*window
                x = 0
                while x+window <= shp[-1]:
                    x_ = x*window
                    agg[z,y,x] = numpy.sum(dat[z,y_:y_+window,x_:x_+window])
                    x+=1
                y+=1
    return agg



