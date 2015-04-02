#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
"""

import os
import argparse
from datetime import datetime
from l2d import create_dems, create_vrts


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('fnames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='+', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='+', default=[])
    # parser.add_argument('--chm', help='Create CHM from DTM and DSM', default=False, action='store_true')
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--bounds', help='Bounds (xmin,xmax,ymin,ymax) of output files (VRTs)', default=None, nargs=4)
    parser.add_argument('--outdir', help='Output directory', default='')
    args = parser.parse_args()

    numfiles = len(args.fnames)
    print 'Processing %s files' % numfiles
    for i, f in enumerate(args.fnames):
        start = datetime.now()

        # figure out bounds
        """
        bname = os.path.basename(os.path.splitext(f)[0]).split('_')[0]
        b = os.path.basename(bname).split('-')
        x = float(b[0]) + 0.5
        y = float(b[1]) + 0.5
        bounds = "([%s,%s],[%s,%s])" % (x, x + 499, y, y + 499)
        """

        create_dems(os.path.abspath(f), args.dsm, args.dtm, args.epsg, outdir=args.outdir)

        print 'Processed (%s of %s) %s in %s' % (i + 1, numfiles, f, datetime.now() - start)
    create_vrts(args.outdir)
