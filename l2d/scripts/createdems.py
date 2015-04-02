#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
"""

import os
import argparse
import glob
from datetime import datetime
from l2d import create_dems, create_vrts, create_chm, gap_fill


def run(filenames, dsm, dtm, epsg, bounds, outdir):
    """ Process files to create DEMS """
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    demdir = os.path.join(outdir, 'DEMs')
    numfiles = len(filenames)
    print 'Processing %s LAS files into DEMs' % numfiles
    for i, f in enumerate(filenames):
        start = datetime.now()

        create_dems(os.path.abspath(f), dsm, dtm, epsg, outdir=outdir)

        print 'Processed (%s of %s) %s in %s' % (i + 1, numfiles, f, datetime.now() - start)

    print 'Creating VRT files'
    create_vrts(demdir, bounds=bounds)

    print 'Gap-filling and creating final DEMs'
    # create gap-filled versions of DSM and DTM
    dsm_pattern = glob.glob(os.path.join(demdir, 'DSM*max.vrt'))
    dtm_pattern = glob.glob(os.path.join(demdir, 'DTM*idw.vrt'))
    dsm = gap_fill(dsm_pattern, os.path.join(outdir, 'DSM.tif'), interpolation='nearest')
    dtm = gap_fill(dtm_pattern, os.path.join(outdir, 'DTM.tif'), interpolation='nearest')

    # create CHM
    chm = create_chm(dtm, dsm, os.path.join(outdir, 'CHM.tif'))

    # create hillshades
    for f in [dsm, dtm, chm]:
        cmd = 'gdaldem hillshade %s %s' % (f, os.path.splitext(f)[0] + '_hillshade.tif')
        os.system(cmd)


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('fnames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--bounds', help='Bounds (xmin,xmax,ymin,ymax) of output files (VRTs)', default=None, nargs=4)
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    run(args.fnames, args.dsm, args.dtm, args.epsg, args.bounds, args.outdir)


if __name__ == "__main__":
    main()
