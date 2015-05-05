#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
LAS files will be merged together as a single point cloud for processing
"""

import os
import argparse
from datetime import datetime
from l2d import add_filter_parsers, check_overlap, create_dems
import gippy
import ogr
from math import floor, ceil


def main():
    """ Main function for argument parsing """
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('filenames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('-r', '--radius', help='Create DSM (run for each provided radius)', nargs='*', default=['0.56'])
    parser.add_argument('-s', '--site', help='Shapefile in LAS projection', default=None)
    parser.add_argument('-f', '--features', help='Process by these features (polygons)', default=None)
    #parser.add_argument('--tileindex', help='Shapefile of LAS tile extents in polygon', default=None)
    parser.add_argument('--outdir', help='Output directory', default='./')
    parser.add_argument('--suffix', help='Suffix to append to output', default='')
    parser.add_argument('-c', '--clip', help='Align and clip to site shapefile', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help='Print additional info', default=False, action='store_true')
    add_filter_parsers(parser)
    args = parser.parse_args()

    start = datetime.now()

    # vectors
    site = None if args.site is None else gippy.GeoVector(args.site)
    features = None if args.features is None else gippy.GeoVector(args.features)
    # use features from processing polygon if provided, otherwise use site
    features = site if features is None else features
    # TODO - clip each feature to site boundary
    
    # make sure outdir exists
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    del args.site
    del args.features
    create_dems('dsm', features=features, site=site, **vars(args))
    print args

    print 'Completed in %s' % (datetime.now() - start)


if __name__ == "__main__":
    main()
