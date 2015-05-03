#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
import argparse
from datetime import datetime
from l2d import create_density_image, check_boundaries
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

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    start0 = datetime.now()

    # only use files that intersect with site
    site = None if args.site is None else gippy.GeoVector(args.site) 
    if args.site is not None:
        filenames = check_boundaries(args.filenames, site)
    else:
        filenames = args.filenames

    print 'Creating density image with %s files' % len(filenames)

    fout = create_density_image(filenames, site, points=args.points, outdir=args.outdir, clip=args.clip)

    print 'Created %s in %s' % (fout, datetime.now() - start0)


if __name__ == '__main__':
    main()
