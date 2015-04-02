#!/usr/bin/env python

"""
This processes a series of DSM and DTM files to gap fill and create hillshaded versions
"""

import os
import argparse
import glob
from l2d import gap_fill, create_chm


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final gap-filled DEMs from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    #parser.add_argument('fnames', help='DTM files to use', nargs='+')
    #parser.add_argument('--fout', help='Output filename', default='DEM.tif')
    parser.add_argument('--outdir', help='Output directory', default='./')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    #parser.add_argument('--bounds', help='Bounds (xmin xmax ymin ymax)', default=None, nargs=4)
    args = parser.parse_args()

    # gap fill DSM and DTM
    dsm = gap_fill(glob.glob('DSM*max.vrt'), os.path.join(args.outdir, 'DSM.tif'), interpolation=args.interp)
    dtm = gap_fill(glob.glob('DTM*idw.vrt'), os.path.join(args.outdir, 'DTM.tif'), interpolation=args.interp)

    # create CHM
    chm = create_chm(dtm, dsm, os.path.join(args.outdir, 'CHM.tif'))

    # create hillshades
    for f in [dsm, dtm, chm]:
        cmd = 'gdaldem hillshade %s %s' % (f, os.path.splitext(f)[0] + '_hillshade.tif')
