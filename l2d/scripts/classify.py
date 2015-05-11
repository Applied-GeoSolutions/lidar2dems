#!/usr/bin/env python

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
import glob
from datetime import datetime
from l2d import find_lasfiles, classify
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('lasdir', help='Directory of LAS file(s) to classify')
    parser.add_argument('-s', '--site', help='Polygon(s) to process', default=None)
    parser.add_argument('--slope', help='Slope (override)', default=None)
    parser.add_argument('--cellsize', help='Cell Size (override)', default=None)
    parser.add_argument('--outdir', help='Output directory location', default='./')
    h = 'Decimate the points (steps between points, 1 is no pruning'
    parser.add_argument('--decimation', help=h, default=None)
    parser.add_argument('-v', '--verbose', help='Print additional info', default=False, action='store_true')

    args = parser.parse_args()

    start = datetime.now()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    if args.site is not None:
        site = gippy.GeoVector(args.site)
    else:
        site = [None]

    fouts = []
    for feature in site:
        filenames = find_lasfiles(args.lasdir, site=feature)
        fout = classify(filenames, site=feature, decimation=args.decimation, 
                        slope=args.slope, cellsize=args.cellsize,
                        outdir=args.outdir, verbose=args.verbose)
        fouts.append(fout)

    print 'Completed in %s' % (datetime.now() - start)


if __name__ == '__main__':
    main()
