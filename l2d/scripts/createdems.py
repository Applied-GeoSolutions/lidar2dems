#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
LAS files will be merged together as a single point cloud for processing
"""

import argparse
from datetime import datetime
from l2d import create_dems, check_boundaries
import gippy
from math import floor, ceil


def main():
    """ Main function for argument parsing """
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('filenames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--outliers', help='Filter outliers with this StdDev threshold in the DSM', default=3.0)
    # h = 'Bounds (xmin ymin xmax ymax) of output files (VRTs)'
    # parser.add_argument('--bounds', help=h, default=None, nargs=4, type=float)
    parser.add_argument('-s', '--shapefile', help='Shapefile with bounds', default=None)
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    start = datetime.now()

    # get bounds from shapefile
    if args.shapefile is not None:
        extent = gippy.GeoVector(args.shapefile).Extent()
        bounds = [floor(extent.x0()), floor(extent.y0()), ceil(extent.x1()), ceil(extent.y1())]

    if bounds is not None:
        filenames = check_boundaries(args.filenames, bounds)
    else:
        filenames = args.filenames

    numfiles = len(filenames)
    print 'Processing %s LAS files into DEMs' % numfiles
    create_dems(filenames, args.dsm, args.dtm, epsg=args.epsg,
                bounds=bounds, outliers=args.outliers, outdir=args.outdir)
    print 'Processed in %s' % (datetime.now() - start)


if __name__ == "__main__":
    main()
