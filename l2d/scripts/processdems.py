#!/usr/bin/env python

"""
This processes a series of DSM and DTM files to gap fill and create hillshaded versions
"""

import os
import argparse
import glob
from l2d import gap_fill, create_chm


def run(indir, outdir, interpolation):
    """ Process series of DEMs from input directory and create final products in output directory """
    # gap fill DSM and DTM
    dsm_pattern = glob.glob(os.path.join(indir, 'DSM*max.vrt'))
    dtm_pattern = glob.glob(os.path.join(indir, 'DTM*idw.vrt'))
    dsm = gap_fill(dsm_pattern, os.path.join(outdir, 'DSM.tif'), interpolation=interpolation)
    dtm = gap_fill(dtm_pattern, os.path.join(outdir, 'DTM.tif'), interpolation=interpolation)

    # create CHM
    chm = create_chm(dtm, dsm, os.path.join(outdir, 'CHM.tif'))

    # create hillshades
    for f in [dsm, dtm, chm]:
        cmd = 'gdaldem hillshade %s %s' % (f, os.path.splitext(f)[0] + '_hillshade.tif')
        os.system(cmd)


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('--indir', help='Input directory containing DEMs', default='./')
    parser.add_argument('--outdir', help='Output directory', default='./')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    args = parser.parse_args()

    run(args.indir, args.outdir, args.interp)


if __name__ == "__main__":
    main()
