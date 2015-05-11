#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
from datetime import datetime
import glob
from l2d import find_lasfiles, create_dems, gap_fill
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

    # loop through features
    fouts_site = []
    products = dem_products(args.demtype)
    bnames = {p: '%s%s.%s' % (args.demtype, args.suffix, p) for p in products}
    for feature in site: 
        # get classified las filename
        if args.demtype == 'density':
            # find all las files within feature
            lasfiles = find_lasfiles(args.lasdir, site=feature)
        else:
            # assume single classified las file exists for this feature
            lasfiles = [glob.glob(os.path.join(args.lasdir, feature.Basename() + '*.las'))[0]]
        print lasfiles

        # pull out the arguments to pass to create_dems
        keys = ['radius', 'decimation', 'maxsd', 'maxz', 'maxangle', 'returnnum', 
                'outdir', 'suffix', 'verbose']
        vargs = vars(args)
        kwargs = {k:vargs[k] for k in vargs if k in keys}

        # create the dems
        try:
            fouts = create_dems(lasfiles, args.demtype, site=feature, **kwargs)
            print fouts
        except Exception, e:
            if args.verbose:
                print traceback.format_exc()
            print 'Error creating %s: %s' % (args.demtype, e)
            exit(2)

        # gap-fill each product (except density)
        if args.gapfill and args.demtype != 'density':
            _fouts = {}
            for product in fouts[0].keys():
                print product
                if product == 'den':
                    continue
                # input filenames
                fnames = [f[product] for f in fouts]
                # output filename
                bname = if feature is None else feature.Basename() + '_'
                fout = os.path.join(args.outdir, bname + bnames[product] + '.tif')
                gap_fill(fnames, fout, site=feature)
                _fouts[product] = [fout]
            fouts = _fouts

        print fouts

        fouts_site.append(fouts)

    print fouts_site

    # combine all polygons into single file and align to site
    fouts = {}
    for product in fouts_site[0].keys():
        fnames = [f[product] for f in fouts_site]
        fout = os.path.join(args.outdir, '%s%s.%s.tif' % args.demtype, args.suffix, product)
        combine(fnames, fout, site=site)
        fouts[product] = fout

    print fouts

    print 'Completed %s (%s) in %s' % (args.demtype, args.outdir, datetime.now() - start0)


if __name__ == '__main__':
    main()
