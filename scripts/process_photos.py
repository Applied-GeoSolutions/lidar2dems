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

# WGS-84/UTM EPSG codes
epsg_codes = {
    '49N': 32649,
    '49S': 32749,
    '50N': 32650,
    '50S': 32750
}

def geotag(files, shapefile, attr, epsg='4326', res='0.5', outdir=None):
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
                [img.XSize()-1, 0, x[2], y[2]],
                [img.XSize()-1, img.YSize()-1, x[3], y[3]],
                [0, img.YSize()-1, x[0], y[0]] ])
            proj = shp.Projection()
            img.SetGCPs(gcps, proj)
            img = None

            # warp to new file
            bname, ext = os.path.splitext(fname)
            EPSG = 'EPSG:%s' % epsg
            if outdir is not None:
                bname = os.path.join(outdir, os.path.basename(bname))
            fout = '%s_EPSG%s%s' % (bname, epsg, ext)
            if not os.path.exists(fout):
                print 'Updating ', bname
                cmd = 'gdalwarp %s %s -t_srs EPSG:%s -tr %s %s -dstnodata "0"' % (fname, fout, epsg, res, res)
                print cmd
                os.system(cmd)

                # add overviews
                img = gippy.GeoImage(fout, True)
                img.AddOverviews()
                img = None

                print 'Created %s' % fout


def main():
    """ main """

    outdir = 'photos'

    # each spec
    specs = glob.glob('spec*')
    for spec in ['spec2']: #specs:
        print spec
    #for spec in ['spec5']:
        polygons = [f for f in glob.glob(os.path.join(spec, 'Polygon_*')) if os.path.isdir(f)]
        for poly in polygons:
            dout = os.path.join('photos', basename(poly))
            mkdir(dout)
            for datedir in [f for f in glob.glob(os.path.join(poly,'*')) if os.path.isdir(f)]:
                # link shapefile
                shpfiles = glob.glob(os.path.join(datedir, 'photo-footprint', 'field_photo_coverage.*'))
                for s in shpfiles:
                    bname, ext = os.path.splitext(os.path.basename(s))
                    fout = os.path.join(dout, bname + '_' + basename(datedir) + ext)
                    if ext == '.shp':
                        shpfile = fout
                    link(s, fout, hard=True)
                # create geotagged and downsampled photos
                images = glob.glob(os.path.join(datedir, 'image', '*', '*.tif'))
                print shpfile
                geotag(images, shpfile, "IMAGE", epsg=str(epsg_codes[poly[-3:]]), outdir=dout)
                
    
    #link_photos('spec1/Polygon_015_utm_50N/141020', 'photos/Polygon_015_utm_50N/')




if __name__ == "__main__":
    main()
    
