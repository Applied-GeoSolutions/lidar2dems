#!/usr/bin/env python

"""
Combined a series of DEM and gap fill.  Optionally regrid using provided shapefile
"""

import argparse
import datetime as dt
from l2d import gap_fill, create_hillshade
from gippy import GeoVector


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs using multiple radius versions if provided'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('filenames', help='DEM files to combine and fill', nargs='+')
    h = 'Clip final image to this shapefile'
    parser.add_argument('-s', '--site', help=h, default=None)
    parser.add_argument('--fout', help='Output filename', default='DEM.tif')
    parser.add_argument('--hillshade', help='Generate hillshade', default=False, action='store_true')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    parser.add_argument('-c', '--clip', help='Align and clip to site file', action='store_true', default=False)
    args = parser.parse_args()

    start = dt.datetime.now()
    print 'Gap-filling and creating final DEMs from %s files' % len(args.filenames)
    site = None if args.site is None else GeoVector(args.site)

    fout = gap_fill(args.filenames, args.fout, site=site, interpolation=args.interp)

    if args.hillshade:
        create_hillshade(fout)

    print 'Completed in %s' % (dt.datetime.now() - start)


if __name__ == "__main__":
    main()
