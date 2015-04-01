#!/usr/bin/env python

import argparse
import gippy
import numpy
from scipy.interpolate import griddata


def gap_fill(filenames, fout, interpolation='nearest'):
    """ Gap fill from higher radius DTMs, then fill remainder with interpolation """
    filenames = sorted(filenames)
    imgs = gippy.GeoImages(filenames)
    nodata = imgs[0][0].NoDataValue()
    arr = imgs[0][0].Read()

    for i in range(1, imgs.size()):
        locs = numpy.where(arr == nodata)
        arr[locs] = imgs[i][0].Read()[locs]

    # linear interpolation at bad points
    goodlocs = numpy.where(arr != nodata)
    badlocs = numpy.where(arr == nodata)
    arr[badlocs] = griddata(goodlocs, arr[goodlocs], badlocs, method=interpolation)

    # write output
    imgout = gippy.GeoImage(fout, imgs[0])
    imgout.SetNoData(nodata)
    imgout[0].Write(arr)
    return imgout


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Create final DTM from multiple DTM using different radius gridding'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('fnames', help='DTM files to use', nargs='+')
    parser.add_argument('--fout', help='Output filename', default='DEM.tif')
    parser.add_argument('--interp', help='Interpolation method (nearest, linear, cubic)', default='nearest')
    args = parser.parse_args()

    gap_fill(args.fnames, args.fout, interpolation=args.interp)
