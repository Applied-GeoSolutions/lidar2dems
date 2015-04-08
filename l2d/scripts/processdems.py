#!/usr/bin/env python

"""
This processes a series of DSM and DTM files to gap fill and create hillshaded versions
"""

import os
import argparse
import datetime as dt
import glob
import gippy
from l2d import gap_fill, create_chm


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('--indir', help='Input directory containing DEMs', default='./')
    parser.add_argument('--outdir', help='Output directory', default='./')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    parser.add_argument('-v', '--verbose', help='Verbosity level', type=int, default=1)
    args = parser.parse_args()

    start = dt.datetime.now()
    gippy.Options.SetVerbose(args.verbose)
    print 'Gap-filling and creating final DEMs'

    # create gap-filled versions of DSMs
    dsm_files = glob.glob(os.path.join(args.indir, 'DSM*max.tif'))
    dsm = gap_fill(dsm_files, os.path.join(args.outdir, 'DSM.tif'), interpolation=args.interp)

    # create gap-filled versions of DTMs
    dtm_files = glob.glob(os.path.join(args.indir, 'DTM*idw.tif'))
    dtm = gap_fill(dtm_files, os.path.join(args.outdir, 'DTM.tif'), interpolation=args.interp)

    # create CHM
    chm = create_chm(dtm, dsm, os.path.join(args.outdir, 'CHM.tif'))

    # create hillshades
    for f in [dsm, dtm, chm]:
        cmd = 'gdaldem hillshade %s %s' % (f, os.path.splitext(f)[0] + '_hillshade.tif')
        os.system(cmd)

    print 'Processed in %s' % (dt.datetime.now() - start)


if __name__ == "__main__":
    main()
