#!/usr/bin/env python

# this processes a directory tree of photos collected by SurTech along with lidar
# for each file it assigns a footprint retrieved from a shapefile, then warps it into output directory

import os
import glob
import numpy
import gippy
from gips.utils import basename, mkdir, link
from shapely.wkt import loads
import traceback
from ntpath import basename as ntbasename
import argparse

# WGS-84/UTM EPSG codes
epsg_codes = {
    '49N': 32649,
    '49S': 32749,
    '50N': 32650,
    '50S': 32750
}


def geotag(files, shapefile, attr, epsg='4326', res=0.5, outdir=''):
    """ Geotag all these files using the given attribute in the shapefile """
    outdir = os.path.abspath(outdir)
    mkdir(outdir)
    shp = gippy.GeoVector(shapefile)
    geoms = {}
    # cycle through features and load them up
    attrs = shp.Attributes()
    if attr not in attrs:
        print 'LINK'
        attr = 'LINK'

    for f in shp:
        fname = ntbasename(f[attr])
        geoms[fname] = loads(f.WKT()).exterior.coords[:]

    for fname in files:
        bname = os.path.basename(fname)
        if bname in geoms.keys():
            coords = geoms[bname]

            try:
                # add gcps and set projection
                img = gippy.GeoImage(fname, True)
            except:
                print 'Error reading %s' % fname
                continue
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            gcps = numpy.array([
                [0, 0, x[1], y[1]],
                [img.XSize() - 1, 0, x[2], y[2]],
                [img.XSize() - 1, img.YSize() - 1, x[3], y[3]],
                [0, img.YSize() - 1, x[0], y[0]]])
            proj = shp.Projection()
            img.SetGCPs(gcps, proj)
            img = None

            # warp to new file
            bname, ext = os.path.splitext(fname)
            bname = os.path.basename(bname)
            fout = os.path.join(outdir, '%s_EPSG%s%s' % (bname, epsg, ext))
            if not os.path.exists(fout):
                print 'Updating ', bname
                cmd = 'gdalwarp %s %s -t_srs EPSG:%s -tr %s %s -dstnodata "0"' % (fname, fout, epsg, res, res)
                print cmd
                continue
                os.system(cmd)

                # add overviews
                img = gippy.GeoImage(fout, True)
                img.AddOverviews()
                img = None

                print 'Created %s' % fout


def process_photos(indir, outdir='', subdir='photos', res=0.5):
    # create output directory with this same Polygon name if it doesn't exist
    dout = os.path.join(outdir, basename(indir))
    mkdir(dout)

    # loop through child directories (date directories)
    for datedir in [f for f in glob.glob(os.path.join(indir, '*')) if os.path.isdir(f)]:
        # link the shapefiles
        shpfiles = glob.glob(os.path.join(datedir, 'photo-footprint', 'field_photo_coverage.*'))
        for s in shpfiles:
            bname, ext = os.path.splitext(os.path.basename(s))
            fout = os.path.join(dout, bname + '_' + basename(datedir) + ext)
            if ext == '.shp':
                shpfile = fout
            link(s, fout, hard=True)

        dout2 = os.path.join(dout, subdir)
        mkdir(dout2)
        # create geotagged and downsampled photos
        images = glob.glob(os.path.join(datedir, 'image', '*', '*.tif'))
        geotag(images, shpfile, "IMAGE", epsg=str(epsg_codes[d[-3:]]), res=res, outdir=dout2)


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Geotag photos', formatter_class=dhf)
    parser.add_argument('directories', nargs='+', help='Polygon directories to geotag')
    parser.add_argument('--dout', help='Top-level directory to output photos to')
    parser.add_argument('--subdir', help='Create a directory for photos under the output directory', default='photos')
    parser.add_argument('--res', help='Resolution of output photos', default=0.5)
    args = parser.parse_args()

    if args.dout != '':
        mkdir(args.dout)

    # directories of the form Polygon_XXX_utm_YYY where XXX is polgyon number and YYY is the utm zone
    for d in args.directories:
        process_photos(d, args.dout, res=args.res)
