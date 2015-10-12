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
Creates density image of all files
"""

import os
from datetime import datetime
from l2d.pdal import create_dems
from l2d.utils import find_lasfiles, find_classified_lasfile, dem_products, class_params, create_vrt
from l2d.parsers import l2dParser
from gippy import GeoVector


def main():
    parser = l2dParser(description='Create DEM(s) from LiDAR files', commands=True)
    parser.add_input_parser()
    parser.add_output_parser()
    parser.add_filter_parser()
    parser.add_argument('--vendor_classified', 
	help='Files are not classified by l2d, the l2d naming scheme was not used for classified files', 
	default=False)
    args = parser.parse_args()

    start0 = datetime.now()

    lasdir = args.lasdir

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
    products = dem_products(args.demtype)
    bnames = {p: '%s%s.%s' % (args.demtype, args.suffix, p) for p in products}
    prefix = ''  # if args.site is None else site.Basename() + '_'
    fouts = {p: os.path.join(args.outdir, '%s%s%s.%s.vrt' % (prefix, args.demtype, args.suffix, p)) for p in products}

    # pull out the arguments to pass to create_dems
    keys = ['radius', 'decimation', 'maxsd', 'maxz', 'maxangle', 'returnnum',
            'outdir', 'suffix', 'verbose', 'overwrite']
    vargs = vars(args)
    kwargs = {k: vargs[k] for k in vargs if k in keys}

    # run if any products are missing
    exists = all([os.path.exists(f) for f in fouts.values()])
    if exists and not args.overwrite:
        print 'Already created %s in %s' % (args.demtype, os.path.relpath(args.outdir))
        exit(0)

    # loop through features
    pieces = []
    for feature in site:
        try:
	    # find las files
	    if args.demtype == 'density':
	        lasfiles = find_lasfiles(args.lasdir, site=feature, checkoverlap=True)
  	    else:
		if vendor_classified == False:
	            lasfiles = find_classified_lasfile(args.lasdir, site=feature, params=class_params(feature))
		else:
		    lasfiles = find_lasfiles(args.lasdir, site=feature, checkoverlap=True)
	    # create dems
	    pouts = create_dems(lasfiles, args.demtype, site=feature, gapfill=args.gapfill, **kwargs)
	    # NOTE - if gapfill then fouts is dict, otherwise is list of dicts (1 for each radius)
	    pieces.append(pouts)
        except Exception, e:
	    print "Error creating %s %s: %s" % (args.demtype, '' if feature is None else feature.Basename(), e)
	    if args.verbose:
	        import traceback
	        print traceback.format_exc()

    # combine all features into single file and align to site
    for product in products:
        # there will be mult if gapfill False and multiple radii....use 1st one
        fnames = [piece[product] for piece in pieces]
        if len(fnames) > 0:
	    create_vrt(fnames, fouts[product], site=site)


    print 'l2d_dems %s completed (%s) in %s' % (args.demtype, os.path.relpath(args.outdir), datetime.now() - start0)


if __name__ == '__main__':
    main()
