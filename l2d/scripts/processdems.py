#!/usr/bin/env python

"""
This processes a series of DSM and DTM files to gap fill and create hillshaded versions
"""

import os
import argparse
import datetime
import glob
from l2d import gap_fill, create_chm


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('--indir', help='Input directory containing DEMs', default='./')
    parser.add_argument('--outdir', help='Output directory', default='./')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    args = parser.parse_args()

    start = datetime.now()
    print 'Gap-filling and creating final DEMs'

    # create gap-filled versions of DSMs
    dsm_files = glob.glob(os.path.join(args.indir, 'DSM*max.vrt'))
    dsm = gap_fill(dsm_files, os.path.join(args.outdir, 'DSM.tif'), interpolation=args.interp)

    # create gap-filled versions of DTMs
    dtm_files = glob.glob(os.path.join(args.indir, 'DTM*idw.vrt'))
    dtm = gap_fill(dtm_files, os.path.join(args.outdir, 'DTM.tif'), interpolation=args.interp)

    # create CHM
    chm = create_chm(dtm, dsm, os.path.join(args.outdir, 'CHM.tif'))

    # create hillshades
    for f in [dsm, dtm, chm]:
        cmd = 'gdaldem hillshade %s %s' % (f, os.path.splitext(f)[0] + '_hillshade.tif')
        os.system(cmd)

    print 'Processed in %s' % (datetime.now() - start)


if __name__ == "__main__":
    main()
