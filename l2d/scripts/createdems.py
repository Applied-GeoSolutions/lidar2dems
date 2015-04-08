#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
LAS files will be merged together as a single point cloud for processing
"""

import argparse
from datetime import datetime
from l2d import create_dems


def main():
    """ Main function for argument parsing """
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('filenames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--outliers', help='Filter outliers with this StdDev threshold in the DSM', default=3.0)
    parser.add_argument('--bounds', help='Bounds (xmin ymin xmax ymax) of output files (VRTs)', default=None, nargs=4)
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    start = datetime.now()
    numfiles = len(args.filenames)
    print 'Processing %s LAS files into DEMs' % numfiles
    create_dems(args.filenames, args.dsm, args.dtm, epsg=args.epsg,
                bounds=args.bounds, outliers=args.outliers, outdir=args.outdir)
    print 'Processed in %s' % (datetime.now() - start)


if __name__ == "__main__":
    main()
