#!/usr/bin/env python

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
import glob
from datetime import datetime
from l2d import class_params, classify
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('directory', help='Directory of LAS file(s) to classify')
    #parser.add_argument('-s', '--site', help='Site to constrain LAS files to', default=None)
    parser.add_argument('-f', '--features', help='Features to classify by', default=None)
    parser.add_argument('--slope', help='Slope', default=1.0)
    parser.add_argument('--cellsize', help='Cell Size', default=3.0)
    parser.add_argument('--outdir', help='Output directory location', default='./')
    parser.add_argument('-v', '--verbose', help='Print additional info', default=False, action='store_true')

    args = parser.parse_args()

    start = datetime.now()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    if args.features is not None:
        args.features = gippy.GeoVector(args.features)

    fouts = []
    for f in args.features:
        # get land use class from feature if available
        try:
            cls = f['class']
        except:
            cls = None
        params = class_params(cls)
        classify(args.directory, site=f, 
                 slope=params[0], cellsize=params[1], 
                 outdir=args.outdir, verbose=args.verbose)

    print 'Completed in %s' % (datetime.now() - start)


if __name__ == '__main__':
    main()
