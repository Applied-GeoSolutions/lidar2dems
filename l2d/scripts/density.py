#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
import argparse
from datetime import datetime
from l2d import add_filter_parsers, check_overlap, create_density
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create density image', formatter_class=dhf)
    parser.add_argument('filenames', help='LAS file(s) to include', nargs='+')
    parser.add_argument('--outdir', help='Output directory location', default='./')
    ch=['all', 'ground', 'nonground']
    parser.add_argument('--points', help='Which points to use', choices=ch, default='all')
    h = 'Shapefile in same projection as LiDAR files. Do not process tiles outside this area'
    parser.add_argument('-s','--site', help=h, default=None)
    parser.add_argument('-c','--clip', help='Align to grid and clip to site', default=False, action='store_true')
    parser.add_argument('--suffix', help='Suffix to append to output file', default='')
    parser.add_argument('-v', '--verbose', help='Print additional output', default=False, action='store_true')
    add_filter_parsers(parser)

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    start0 = datetime.now()

    # only use files that intersect with site
    site = None if args.site is None else gippy.GeoVector(args.site) 
    if args.site is not None:
        filenames = check_overlap(args.filenames, site)
    else:
        filenames = args.filenames

    print 'Creating density image with %s files' % len(filenames)

    del args.filenames
    del args.site
    fout = create_density(filenames, site, **vars(args))

    print 'Created %s in %s' % (fout, datetime.now() - start0)


if __name__ == '__main__':
    main()
