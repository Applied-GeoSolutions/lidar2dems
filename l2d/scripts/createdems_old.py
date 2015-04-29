#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
LAS files will be merged together as a single point cloud for processing
"""

import argparse
from datetime import datetime
from l2d import create_dems2, check_boundaries
import gippy


def main():
    """ Main function for argument parsing """
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('filenames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--outliers', help='Filter outliers with this StdDev threshold in the DSM', default=3.0)
    parser.add_argument('--maxangle', help='Filter out points whose absolute value of scan angle is larger', default=None)
    parser.add_argument('-s', '--shapefile', help='Shapefile with correct projection and desired bounds', required=True)
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    start = datetime.now()

    # open vector file
    vector = gippy.GeoVector(args.shapefile)

    # filter out list with only intersecting files
    filenames = check_boundaries(args.filenames, vector)

    numfiles = len(filenames)
    print 'Processing %s LAS files into DEMs' % numfiles
    create_dems2(filenames, args.dsm, args.dtm, vector=vector,
                 outliers=args.outliers, maxangle=args.maxangle, outdir=args.outdir)

    print 'Processed in %s' % (datetime.now() - start)


if __name__ == "__main__":
    main()
