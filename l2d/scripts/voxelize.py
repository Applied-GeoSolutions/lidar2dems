#!/usr/bin/env python
################################################################################
#   lidar2dems - utilties for creating DEMs from LiDAR data
#
#   AUTHOR: Matthew Hanson, matt.a.hanson@gmail.com
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

"""
Creates raster of return or intensity counts in cubic meter voxels
"""

import os
from datetime import datetime
import argparse
from l2d.voxel_utils import create_voxels
from l2d.utils import find_lasfiles, find_classified_lasfile, create_vrt, class_params
from l2d.parsers import l2dParser
from gippy import GeoVector

def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Voxelize lidar data to output rasters'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument(
        'lasdir', help='Directory holding classified LAS files')
    parser.add_argument(
	'demdir', help='Directory holding DEMs (including DSM and DTM for each feature)')
    parser.add_argument(
	'--voxtypes', help='Type of return data in output voxels (e.g. counts, intensity)', nargs='*', default=['count','intensity'])
    parser.add_argument(
        '-s', '--site', default=None,
        help='Site shapefile name (use if used for DTM/DSM creation); if area of interest is smaller than whole scene, l2d_dems should be run 			again using voxel region of interest shapefile')
    parser.add_argument(
	    '--vendor_classified', 
	    help='Files are not classified by l2d, the l2d naming scheme was not used for classified files', default=False)
    parser.add_argument('--slope', help='Slope (override)', default=None)
    parser.add_argument('--cellsize', help='Cell Size (override)', default=None)
    parser.add_argument(
	'--outdir', help='Directory to output voxel rasters')
    parser.add_argument(
        '-o', '--overwrite', default=False, action='store_true',
        help='Overwrite any existing output files')
    parser.add_argument(
        '-v', '--verbose', default=False, action='store_true',
        help='Print additional info')
    args = parser.parse_args()

    start0 = datetime.now()

    # open site vector
    if args.site is not None:
        try:
            site = GeoVector(args.site)
        except:
            print 'Error opening %s' % args.site
            exit(2)
    else:
        site = [None]

    # make sure outdir exists
    args.outdir = os.path.abspath(args.outdir)
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    args.lasdir = os.path.abspath(args.lasdir)

    # the final filenames
    products = args.voxtypes
    fouts = {p: os.path.join(args.outdir, '%s.voxels.vrt' % (p)) for p in products}

    # run if any products are missing
    exists = all([os.path.exists(f) for f in fouts.values()])
    if exists and not args.overwrite:
        print 'Already created %s in %s' % (args.voxtypes, os.path.relpath(args.outdir))
        exit(0)

    # loop through features
    pieces = []
    for feature in site:
        try:
	    # find las files
	    if args.vendor_classified == False:
		parameters = class_params(feature, args.slope, args.cellsize)
	        lasfiles = find_classified_lasfile(args.lasdir, site=feature, params=parameters)
	    else:
		lasfiles = find_lasfiles(args.lasdir, site=feature, checkoverlap=True)
	    # create voxels - perhaps not loop over features, but instead voxelize each tile...for loop over lasfiles here. would need to determine output image dimensions though since they could no longer be pulled from existing feature geotiff.
	    pouts = create_voxels(lasfiles, voxtypes=args.voxtypes, demdir=args.demdir, site=feature, 
			outdir=args.outdir, overwrite=args.overwrite)
	    pieces.append(pouts)
        except Exception, e:
	    print "Error creating voxels: %s" % e
	    if args.verbose:
	        import traceback
	        print traceback.format_exc()

    # combine all features into single file and align to site
    # for product in products:
    #     fnames = [piece[product] for piece in pieces]
    #     if len(fnames) > 0:
# 	    create_vrt(fnames, fouts[product], site=site)


    print 'l2d_voxelize completed (%s) in %s' % (os.path.relpath(args.outdir), datetime.now() - start0)


if __name__ == '__main__':
    main()
