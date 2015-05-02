#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
import argparse
from datetime import datetime
from l2d import create_density_image
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create density image', formatter_class=dhf)
    parser.add_argument('filenames', help='LAS file(s) to include', nargs='+')
    parser.add_argument('--outdir', help='Output directory location', default='./')
    ch=['all', 'ground', 'nonground']
    parser.add_argument('--points', help='Which points to use', choices=ch, default='all')
    parser.add_argument('-s','--site', help='Site shapefile in same projection as LiDAR files', default=None)
    parser.add_argument('-c','--clip', help='Align to grid and clip to site')

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    start0 = datetime.now()

    print 'Creating density image with %s files' % len(args.filenames)

    site = None if args.site is None else gippy.GeoVector(args.site) 
    fout = create_density_image(args.filenames, site, points=args.points, outdir=args.outdir, clip=args.clip)

    print 'Created %s in %s' % (fout, datetime.now() - start0)


if __name__ == '__main__':
    main()
