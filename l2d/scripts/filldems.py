#!/usr/bin/env python

"""
Combined a series of DEM and gap fill.  Optionally regrid using provided shapefile
"""

import os
import argparse
import datetime as dt
import gippy
from l2d import warp_image, gap_fill
from math import floor, ceil


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs using multiple radius versions if provided'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('filenames', help='DEM files to combine and fill', nargs='+')
    h = 'If provided use bounds from shapefile to warp input files first'
    parser.add_argument('-s', '--shapefile', help=h, default=None)
    parser.add_argument('--fout', help='Output filename', default='DEM.tif')
    parser.add_argument('--hillshade', help='Generate hillshade', default=False, action='store_true')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    #parser.add_argument('-v', '--verbose', help='Verbosity level', type=int, default=1)
    args = parser.parse_args()

    start = dt.datetime.now()
    #gippy.Options.SetVerbose(args.verbose)
    print 'Gap-filling and creating final DEMs from %s files' % len(args.filenames)

    if args.shapefile is not None:
        extent = gippy.GeoVector(args.shapefile).Extent()
        bounds = [floor(extent.x0()), floor(extent.y0()), ceil(extent.x1()), ceil(extent.y1())]
        filenames = []
        for f in args.filenames:
            warp_image(f, bounds)
    else:
        filenames = args.filenames

    fout = gap_fill(filenames, args.fout, args.interp)

    if args.hillshade:
        cmd = 'gdaldem hillshade %s %s' % (fout, os.path.splitext(fout)[0] + '_hillshade.tif')
        os.system(cmd)

    print 'Processed in %s' % (dt.datetime.now() - start)


if __name__ == "__main__":
    main()
