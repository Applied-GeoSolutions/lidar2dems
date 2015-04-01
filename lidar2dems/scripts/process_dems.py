#!/usr/bin/env python

import argparse
from lidar2dems import gap_fill


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('fnames', help='DTM files to use', nargs='+')
    parser.add_argument('--fout', help='Output filename', default='DEM.tif')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    # Create final

    gap_fill(args.fnames, args.fout, interpolation=args.interp)
