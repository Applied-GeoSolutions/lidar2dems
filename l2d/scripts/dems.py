#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
from datetime import datetime
from l2d import l2dParser, create_dem, create_dem_piecewise, gap_fill
from gippy import GeoVector


def main():
    parser = l2dParser(description='Create DEM(s) from LiDAR files', commands=True)
    parser.add_input_parser()
    parser.add_output_parser()
    parser.add_filter_parser()
    args = parser.parse_args()

    start0 = datetime.now()

    # open vectors
    if args.site is not None:
        try:
            args.site = GeoVector(args.site)[0]
        except:
            print 'Error opening %s' % args.site
            exit(2)
    if args.features is not None:
        try:
            args.features = GeoVector(args.features)
        except:
            print 'Error opening %s' % args.features
            exit(2)

    # make sure outdir exists
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # run piecewise if given processing features
    if args.features is None:
        del args.features
        func = lambda **kwargs: create_dem(**kwargs)
    else:
        func = lambda **kwargs: create_dem_piecewise(**kwargs)

    # create dems for each given radius
    radii = args.radius 
    del args.radius
    gapfill = args.gapfill
    del args.gapfill
    fouts = []
    try:
        for rad in radii:
            fouts.append(func(radius=rad, **vars(args)))
    except Exception, e:
        print 'Error creating %s: %s' % (args.demtype, e)
        exit(2)

    # gap-fill each type of output file
    if gapfill:
        _fouts = []
        for product in fouts[0].keys():
            if product != 'den':
                filenames = [f[product] for f in fouts]
                fout = os.path.join(args.outdir, '%s%s.%s.tif' % (args.demtype, args.suffix, product))
                gap_fill(filenames, fout, site=args.site)
                _fouts.append(fout)
        fouts = _fouts

    print 'Completed %s (%s) in %s' % (args.demtype, args.outdir, datetime.now() - start0)


if __name__ == '__main__':
    main()
