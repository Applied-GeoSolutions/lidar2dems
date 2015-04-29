#!/usr/bin/env python

"""
Creates density image of all files
"""

import os
import argparse
from datetime import datetime
from l2d import create_density_image


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create density image', formatter_class=dhf)
    parser.add_argument('filenames', help='LAS file(s) to include', nargs='+')
    parser.add_argument('--outdir', help='Output directory location', default='./')
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs', required=True)

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    start0 = datetime.now()

    print 'Creating density image with %s files' % len(args.filenames)

    create_density_image(args.filenames, epsg=args.epsg, outdir=args.outdir)

    print 'Completed in %s' % (datetime.now() - start0)


if __name__ == '__main__':
    main()
