#!/usr/bin/env python

# this script can serve as an example for post-processing voxels
# from here, you're on your own!
# note the three critical (and general) steps involved:
# 1. read voxel image to array
# 2. perform aggregation if needed and calculation of region of interest
# 3. output image with calculated metric

"""
Creates raster of transformed relative density models for declared region of interest
"""

from datetime import datetime
import argparse
from l2d.utils import find_lasfiles, find_classified_lasfile, create_vrt, class_params
from l2d.voxel_utils import aggregate, clip_by_site
import os, math, numpy, glob
from scipy import signal, interpolate
import scipy
import gippy

def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Process voxels into relative density metrics; note this script will require modifications for specific calculations, users are responsible for this'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument(
        'voxdir', help='Directory holding voxel lidar data')
    parser.add_argument(
	'--voxtype', help='Type of return data to use for calculations', nargs='*', default=['count'])
    parser.add_argument(
	'--metric', helep='Metric name user defined, used for naming output image', default=None)
    parser.add_argument(
	'--start', help='Low height of relative density region of interest', default=['1'])
    parser.add_argument(
	'--stop', help='Top height of relative density region of interest', default=['5'])
    parser.add_argument(
	'--pixelsize', help='Output image pixel size, used to aggregate voxels in x-y dimension', default=['1'])
    parser.add_argument(
        '-s', '--site', default=None,
        help='Site shapefile name used for ')
    parser.add_argument(
	'--outdir', help='Directory to output metric rasters, directory name should specify type of metric')
    parser.add_argument(
        '-o', '--overwrite', default=False, action='store_true',
        help='Overwrite any existing output files')
    parser.add_argument(
        '-v', '--verbose', default=False, action='store_true',
        help='Print additional info')
    args = parser.parse_args()

    start0 = datetime.now()

    #variables describing region of interest and scale
    startoff = int(args.start)
    cutoff = int(args.stop)
    pixelsize = int(args.pixelsize)
    if args.metric is None:
	args.metric = 'rdm-%s_to_%s' %(startoff,cutoff)

    # make sure outdir exists
    args.outdir = os.path.abspath(args.outdir)
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # the final filenames
    product = args.metric
    fouts = os.path.join(args.outdir, '%s.voxel_metric.vrt' % (product))

    # run if any products are missing
    exists = all([os.path.exists(f) for f in fouts.values()])
    if exists and not args.overwrite:
        print 'Already created metric rasters in %s' % (os.path.relpath(args.outdir))
        exit(0)

    # loop through voxel rasters
    # site = glob.glob('*.%s.*.tif' %(args.voxtype))
    pieces = []
    for feature in site:
        try:

	    # extract naming convention
	    bname = '' if site is None else site.Basename() + '_'
	    ftr = bname.split('_')[0]
	    bname = os.path.join(os.path.abspath(voxdir), '%s' % (bname))
	    vox_name = bname + 'voxels.%s.tif' %(args.voxtype)
	    out = os.path.join(args.outdir, '%s_%s.voxel_metric.tif' % (ftr,product))

	    #open image
	    vox_img = gippy.GeoImage(vox_name)
	    vox_arr = vox_img.Read()
	    nbands,nrows,ncols = vox_arr.shape

	    #calculate relative density ratio of returns
	    data = aggregate(vox_arr,pixelsize)
	    i1 = numpy.sum(data[startoff+1:cutoff+1],axis=0,dtype=float)
	    i2 = numpy.sum(data,axis=0,dtype=float)

	    ratio = numpy.zeros(i1.shape, dtype=float)
	    ratio[numpy.where(i2>0)] = i1[numpy.where(i2>0)]/i2[numpy.where(i2>0)]
	    transformed = numpy.sqrt(ratio)+0.001

	    #output ratio image
	    imgout = gippy.GeoImage(out,vox_img,gippy.GDT_Float32,1)
	    imgout[0].Write(transformed)
	    clip_by_site(out,feature)

	    pieces.append(out)

        except Exception, e:
	    print "Error creating metric: %s" % e
	    if args.verbose:
	        import traceback
	        print traceback.format_exc()

    # combine all features into single file and align to site for chm
    create_vrt(pieces, fouts, site=site)


    print 'l2d_process_voxels completed (%s) in %s' % (os.path.relpath(args.outdir), datetime.now() - start0)


if __name__ == '__main__':
    main()







