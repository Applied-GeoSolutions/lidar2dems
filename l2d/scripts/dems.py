#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
from datetime import datetime
import glob
from l2d import *
from l2d.parsers import l2dParser
from gippy import GeoVector
import traceback


def main():
    parser = l2dParser(description='Create DEM(s) from LiDAR files', commands=True)
    parser.add_input_parser()
    parser.add_output_parser()
    parser.add_filter_parser()
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
    products = dem_products(args.demtype)
    bnames = {p: '%s%s.%s' % (args.demtype, args.suffix, p) for p in products}
    prefix = '' # if args.site is None else site.Basename() + '_'
    fouts = {p: os.path.join(args.outdir, '%s%s%s.%s.vrt' % (prefix, args.demtype, args.suffix, p)) for p in products}

    # pull out the arguments to pass to create_dems
    keys = ['radius', 'decimation', 'maxsd', 'maxz', 'maxangle', 'returnnum', 
            'outdir', 'suffix', 'verbose']
    vargs = vars(args)
    kwargs = {k:vargs[k] for k in vargs if k in keys}

    # run if any products are missing
    run = all([os.path.exists(f) for f in fouts.values()])

    # loop through features
    pieces = []
    for feature in site: 
        # find appropriate files
        if args.demtype == 'density':
            lasfiles = find_lasfiles(args.lasdir, site=feature, checkoverlap=True)
        else:
            lasfiles = find_lasfile(args.lasdir, site=feature, params=class_params(feature))
        if len(lasfiles) == 0:
            print 'No valid LAS files found!'
            exit(2)

        # create the dems
        try:
            pouts = create_dems(lasfiles, args.demtype, site=feature, gapfill=args.gapfill, **kwargs)
        except Exception, e:
            if args.verbose:
                print traceback.format_exc()
            print 'Error creating %s: %s' % (args.demtype, e)
            exit(2)

        # NOTE - if gapfill then fouts is dict, otherwise is list of dicts (1 for each radius)
        pieces.append(pouts)

    # combine all polygons into single file and align to site
    for product in products:
        # there will be mult if gapfill False and multiple radii....use 1st one
        fnames = [piece[product] for piece in pieces]
        combine(fnames, fouts[product], site=site)

    print 'Completed %s (%s) in %s' % (args.demtype, args.outdir, datetime.now() - start0)


if __name__ == '__main__':
    main()
