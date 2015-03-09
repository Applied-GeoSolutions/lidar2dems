#!/usr/bin/env python

import os
import argparse
import math
import numpy
import gippy
from shapely.wkt import loads


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    h = 'Extract geometry from shapefile and assign to raster(s)'
    parser = argparse.ArgumentParser(description=h, formatter_class=dhf)
    parser.add_argument('files', help='Files to apply SRS and Geotransform to', nargs='*')
    parser.add_argument('-s','--shapefile', help='Read in shapefile and loop through features', required=True)
    parser.add_argument('-a', '--attr', help='Attribute holding filename', required=True)
    parser.add_argument('--epsg', help='EPSG to warp on output', default='4326')
    parser.add_argument('--res', help='Resolution of output (in target SRS units)', default='0.5')

    args = parser.parse_args()

    shp = gippy.GeoVector(args.shapefile)
    geom = {}
    # cycle through features
    for f in shp: 
        #feats = shp.where(args.attr, bname)
        fname = os.path.basename(f[args.attr])
        geom[fname] = loads(f.WKT()).exterior.coords[:]

    for fname in args.files:
        bname = os.path.basename(fname)
        if bname in geom.keys():
            print 'Updating ', bname
            coords = geom[bname]
            
            # add gcps and set projection
            img = gippy.GeoImage(fname, True)
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            gcps = numpy.array([
                [0, 0, x[1], y[1]],
                [img.XSize()-1, 0, x[2], y[2]],
                [img.XSize()-1, img.YSize()-1, x[3], y[3]],
                [0, img.YSize()-1, x[0], y[0]] ])
            proj = shp.Projection()
            img.SetGCPs(gcps, proj)
            img = None

            # warp to new file
            bname, ext = os.path.splitext(fname)
            EPSG = 'EPSG:%s' % args.epsg
            fout = '%s_EPSG%s%s' % (bname, args.epsg, ext)
            cmd = 'gdalwarp %s %s -t_srs EPSG:%s -tr %s %s -dstnodata "0"' % (fname, fout, args.epsg, args.res, args.res)
            print cmd
            os.system(cmd)

            # add overviews
            img = gippy.GeoImage(fout, True)
            img.AddOverviews()
            img = None

            print 'Created %s' % fout


if __name__ == '__main__':
    main()
