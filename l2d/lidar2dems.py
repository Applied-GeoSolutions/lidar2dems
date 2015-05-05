#!/usr/bin/env python

# Library functions for creating DEMs from Lidar data

import os
import sys
from lxml import etree
import tempfile
import glob
import gippy
import numpy
import subprocess
import json
import ogr
from datetime import datetime
from math import floor, ceil
from shapely.geometry import box
from shapely.wkt import loads
import commands
import shutil

"""XML Functions"""

def _xml_base(fout, output, radius, site=None):
    """ Create initial XML for PDAL pipeline containing a Writer element """
    xml = etree.Element("Pipeline", version="1.0")
    etree.SubElement(xml, "Writer", type="writers.p2g")
    etree.SubElement(xml[0], "Option", name="grid_dist_x").text = "1.0"
    etree.SubElement(xml[0], "Option", name="grid_dist_y").text = "1.0"
    etree.SubElement(xml[0], "Option", name="radius").text = str(radius)
    etree.SubElement(xml[0], "Option", name="output_format").text = "tif"
    # add EPSG option? - 'EPSG:%s' % epsg
    if site is not None:
        etree.SubElement(xml[0], "Option", name="spatialreference").text = site.Projection()
        # this not yet working in p2g
        #bounds = get_vector_bounds(site)
        #bounds = '([%s, %s], [%s, %s])' % (bounds[0], bounds[2], bounds[1], bounds[3])
        #etree.SubElement(xml[0], "Option", name="bounds").text = bounds
    etree.SubElement(xml[0], "Option", name="filename").text = fout
    for t in output:
        etree.SubElement(xml[0], "Option", name="output_type").text = t
    return xml

##### FILTERS

def _xml_add_pclblock(xml, pclblock):
    """ Add pclblock Filter element by taking in filename of a JSON file """
    _xml = etree.SubElement(xml, "Filter", type="filters.pclblock")
    etree.SubElement(_xml, "Option", name="filename").text = pclblock
    return _xml


def _xml_add_classification_filter(xml, classification, equality="equals"):
    """ Add classification Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "Classification"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name=equality).text = str(classification)
    return fxml


def _xml_add_maxsd_filter(xml, meank=20, thresh=3.0):
    """ Add outlier Filter element and return """
    # create JSON file for performing outlier removal
    j1 = '{"pipeline": {"name": "Outlier Removal","version": 1.0,"filters":'
    json = j1 + '[{"name": "StatisticalOutlierRemoval","setMeanK": %s,"setStddevMulThresh": %s}]}}' % (meank, thresh)
    f, fname = tempfile.mkstemp(suffix='.json')
    os.write(f, json)
    os.close(f)
    return _xml_add_pclblock(xml, fname)


def _xml_add_maxZ_filter(xml, maxZ):
    """ Add max elevation Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "Z"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name="max").text = maxZ
    return fxml


def _xml_add_maxangle_filter(xml, maxabsangle):
    """ Add scan angle Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "ScanAngleRank"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name="max").text = maxabsangle
    etree.SubElement(_xml, "Option", name="min").text = str(-float(maxabsangle))
    return fxml


def _xml_add_scanedge_filter(xml, value):
    """ Add EdgeOfFlightLine Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "EdgeOfFlightLine"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name="equals").text = value
    return fxml


def _xml_add_filters(xml, maxsd=None, maxZ=None, maxangle=None, scanedge=None):
    if maxsd is not None:
        xml = _xml_add_maxsd_filter(xml, thresh=maxsd)
    if maxZ is not None:
        xml = _xml_add_maxZ_filter(xml, maxZ)
    if maxangle is not None:
        xml = _xml_add_maxangle_filter(xml, maxangle)
    if scanedge is not None:
        xml = _xml_add_scanedge_filter(xml, scanedge)
    return xml


def _xml_add_reader(xml, filename):
    """ Add LAS Reader Element and return """
    _xml = etree.SubElement(xml, "Reader", type="readers.las")
    etree.SubElement(_xml, "Option", name="filename").text = os.path.abspath(filename)
    return _xml


def _xml_add_readers(xml, filenames):
    """ Add merge Filter element and readers to a Writer element and return Filter element """
    if len(filenames) > 1:
        fxml = etree.SubElement(xml, "Filter", type="filters.merge")
    else:
        fxml = xml
    for f in filenames:
        _xml_add_reader(fxml, f)
    return fxml


def _xml_print(xml):
    """ Pretty print xml """
    print etree.tostring(xml, pretty_print=True)


def run_pipeline(xml, verbose=False):
    """ Run PDAL Pipeline with provided XML """
    if verbose:
        _xml_print(xml)

    # write to temp file
    f, xmlfile = tempfile.mkstemp(suffix='.xml')
    if verbose:
        print 'Pipeline file: %s' % xmlfile
    os.write(f, etree.tostring(xml))
    os.close(f)

    cmd = [
        'pdal',
        'pipeline',
        '-i %s' % xmlfile,
        '-v4',
    ]
    # out = os.system(' '.join(cmd) + ' 2> /dev/null ')
    out = os.system(' '.join(cmd))
    os.remove(xmlfile)


def add_filter_parsers(parser):
    """ Add a few different filter options to the parser """
    parser.add_argument('--maxsd', help='Filter outliers with this SD threshold', default=None)
    parser.add_argument('--maxangle', help='Filter by maximum absolute scan angle', default=None)
    parser.add_argument('--maxZ', help='Filter by maximum elevation value', default=None)
    parser.add_argument('--scanedge', help='Filter by scanedge value (0 or 1)', default=None)
    return parser

##### Create DEM files

def create_density(filenames, site, clip=False, points='all', 
                   maxsd=None, maxZ=None, maxangle=None, scanedge=None, 
                   outdir='./', suffix='', verbose=False):
    """ Create density image using all points, ground points, or nonground points  """
    ext = '.den.tif'
    bname = os.path.join(os.path.abspath(outdir), 'pts_' + points + suffix)
    if os.path.isfile(bname + ext):
        return bname + ext

    # pipeline
    xml = _xml_base(bname, ['den'], 0.56, site)
    _xml = xml[0]
    _xml = _xml_add_filters(_xml, maxsd, maxZ, maxangle, scanedge)
    if points == 'nonground':
        _xml = _xml_add_classification_filter(_xml, 1, equality='max')
    elif points == 'ground':
        _xml = _xml_add_classification_filter(_xml, 2)
    _xml_add_readers(_xml, filenames)
    run_pipeline(xml, verbose=verbose)

    # align and clip
    if clip and site is not None:
        warp_image(bname + ext, site, clip=clip)
    return bname + ext


def create_dsm(filenames, radius='0.56', site=None, clip=False,
               maxsd=None, maxZ=None, maxangle=None, scanedge=None, 
               outputs=None, outdir='', suffix='', verbose=False):
    """ Create DSM from LAS file(s) """
    demtype = 'DSM'
    bname = os.path.join(os.path.abspath(outdir), '%s_r%s%s' % (demtype, radius, suffix))
    if outputs is None:
        outputs = ['max']

    # pipeline
    xml = _xml_base(bname, outputs, radius, site)
    _xml = xml[0]
    _xml = _xml_add_filters(_xml, maxsd, maxZ, maxangle, scanedge)
    # non-ground points only
    fxml = _xml_add_classification_filter(_xml, 1, equality='max')
    _xml_add_readers(fxml, filenames)
    run_pipeline(xml, verbose=verbose)

    # align and clip
    if clip and site is not None:
        ext = '.tif'
        for t in outputs:
            warp_image(bname + '.' + t + ext, site, clip=clip)

    return bname


def create_dtm(filenames, radius='0.56', site=None, clip=False,
              outputs=None, outdir='', suffix='', verbose=False):
    """ Create DTM from LAS file(s) """
    demtype = 'DTM'
    bname = os.path.join(os.path.abspath(outdir), '%s_r%s%s' % (demtype, radius, suffix))
    if outputs is None:
        outputs = ['min', 'max', 'idw']

    xml = _xml_base(bname, outputs, radius, site)
    # ground points only
    fxml = _xml_add_classification_filter(xml[0], 2)
    _xml_add_readers(fxml, filenames)
    run_pipeline(xml, verbose=verbose)

    # align and clip
    if clip and site is not None:
        ext = '.tif'
        for t in outputs:
            warp_image(bname + '.' + t + ext, site, clip=clip)

    return bname


def create_dems(demtype, filenames, features, radius='0.56', suffix='', **kwargs):
    """ Convenience function to run DSM or DTM by polygon to all radii """
    if demtype.lower() == 'dsm':
        func = create_dsm
    elif demtype.lower() == 'dtm':
        func = create_dtm
    else:
        raise Exception('invalid demtype %s' % demtype)
    # loop through all features
    for i, feature in enumerate(features):
        fnames = check_overlap(filenames, feature)
        # this is to add a naming scheme so DTMs and DSMs do not get overwritten 
        suff = suffix + '_%s_of_%s' % (i, features.size())
        print 'Polygon %s of %s: processing % files' % (i+1, features.size(), len(filenames))
        func(fnames, suffix=suff, **kwargs) 
    # TODO - combine all parts (for each radii)


def create_chm(dtm, dsm, chm):
    """ Create CHM from a DTM and DSM - assumes common grid """
    dtm_img = gippy.GeoImage(dtm)
    dsm_img = gippy.GeoImage(dsm)
    imgout = gippy.GeoImage(chm, dtm_img)
    nodata = dtm_img[0].NoDataValue()
    imgout.SetNoData(nodata)
    dsm_arr = dsm_img[0].Read()
    arr = dsm_arr - dtm_img[0].Read()
    arr[dsm_arr == nodata] = nodata
    imgout[0].Write(arr)
    return imgout.Filename()


def create_hillshade(filename):
    """ Create hillshade image from this file """
    fout = os.path.splitext(filename)[0] + '_hillshade.tif'
    sys.stdout.write('Creating hillshade: ')
    sys.stdout.flush()
    cmd = 'gdaldem hillshade %s %s' % (filename, fout)
    os.system(cmd)
    return fout

##### Transforms and utilities

def warp_image(filename, vector, suffix='_warp', clip=False):
    """ Warp image to given projection, and use bounds if supplied """
    bounds = get_vector_bounds(vector)

    f, fout = tempfile.mkstemp(suffix='.tif')
    fout = os.path.splitext(filename)[0] + suffix + '.tif'
    img = gippy.GeoImage(filename)
    cmd = [
        'gdalwarp',
        filename,
        fout,
        '-te %s' % ' '.join([str(b) for b in bounds]),
        '-dstnodata %s' % img[0].NoDataValue(),
        "-t_srs '%s'" % vector.Projection(),
        '-r bilinear',
    ]
    if clip:
        cmd.append('-cutline %s' % vector.Filename())
        cmd.append('-crop_to_cutline')
        sys.stdout.write('Warping and clipping image: ')
    else:
        sys.stdout.write('Warping image: ')
    sys.stdout.flush()
    out = os.system(' '.join(cmd))
    return fout

##### Geometries and Bouding boxes

def get_meta_data(filename):
    """ Get metadata from lasfile as dictionary """
    cmd = ['pdal', 'info', '--metadata', '--input', os.path.abspath(filename)]
    meta = json.loads(subprocess.check_output(cmd))['metadata'][0]
    return meta


def get_bounds(filename):
    """ Return shapely geometry of bounding box """
    bounds = get_bounding_box(filename)
    return box(bounds[0][0], bounds[0][1], bounds[2][0], bounds[2][1])


def get_bounding_box(filename, min_points=2):
    """ Get bounding box from LAS file """
    meta = get_meta_data(filename)
    mx, my, Mx, My = meta['minx'], meta['miny'], meta['maxx'], meta['maxy']
    if meta['count'] < min_points:
        raise Exception('{} contains only {} points (min_points={}).'
                        .format(filename, meta['count'], min_points))
    bounds = [(mx, my), (Mx, my), (Mx, My), (mx, My), (mx, my)]
    return bounds


def check_overlap(filenames, vector):
    """ Return filtered list of filenames that intersect with vector """
    sitegeom = loads(vector.WKT())
    goodf = []
    for f in filenames:
        try:
            bbox = get_bounds(f)
            if sitegeom.intersection(bbox).area > 0:
                goodf.append(f)
        except:
            pass
    return goodf


def check_overlap2(shp_ftr, tileindexshp):
    """ Compares LAS tile index bounds to sub-polygon site type bounds to return filelist """
    # driver = ogr.GetDriverByName('ESRI Shapefile')
    # src = driver.Open(tileindexshp)
    lyr = tileindexshp.GetLayer()
    sitegeom = shp_ftr.GetGeometryRef()
    filelist = []

    for ftr in lyr:
        tilegeom = ftr.GetGeometryRef()
        # checks distance between site type polygon and tile, if 0 the two geometries overlap
        dist = sitegeom.Distance(tilegeom)

        if dist == 0:
            filelist.append(ftr.GetField(ftr.GetFieldIndex('las_file')))

    lyr.ResetReading()
    return filelist


def create_bounds_file(polygon, outfile):
    """ Create temporary shapefile with site type polygon """
    driver = ogr.GetDriverByName('Shapefile')
    out = driver.CreateDataSource('./tmp.shp')
    lyr = out.CreateLayer('site', geom_type=ogr.wkbPolygon, srs=osr.SpatialReference().ImportFromEPSG(epsg))

    geom = polygon.GetGeometryRef()

    ftr = ogr.Feature(feature_def=lyr.GetLayerDefn())
    ftr.SetGeometry(geom)
    lyr.CreateFeature(ftr)
    ftr.Destroy()
    out.Destroy()

    return './tmp.shp'


def delete_bounds_file():
    """ Delete tmp file """
    os.remove('./tmp.shp')


def get_vector_bounds(vector):
    """ Get vector bounds from GeoVector, on closest integer grid """
    extent = vector.Extent()
    bounds = [floor(extent.x0()), floor(extent.y0()), ceil(extent.x1()), ceil(extent.y1())]
    return bounds


def create_vrt(filenames, fout, bounds=None, overviews=False):
    """ Create VRT called fout from filenames """
    if os.path.exists(fout):
        return
    cmd = [
        'gdalbuildvrt',
        fout,
    ]
    cmd.extend(filenames)
    if bounds is not None:
        cmd.append('-te %s' % (' '.join(bounds)))
    print 'Creating VRT %s' % fout
    os.system(' '.join(cmd))
    if overviews:
        print 'Adding overviews'
        os.system('gdaladdo -ro %s 2 4 8 16' % fout)


def create_vrts(path, bounds=None, overviews=False):
    """ Create VRT for all these tiles / files """
    import re
    import glob
    pattern = re.compile('.*_(D[ST]M_.*).tif')
    fnames = glob.glob(os.path.join(path, '*.tif'))
    names = set(map(lambda x: pattern.match(x).groups()[0], fnames))
    print path
    for n in names:
        print n
        fout = os.path.abspath(os.path.join(path, '%s.vrt' % n))
        files = glob.glob(os.path.abspath(os.path.join(path, '*%s.tif' % n)))
        create_vrt(files, fout, bounds, overviews)


def gap_fill(filenames, fout, shapefile=None, interpolation='nearest'):
    """ Gap fill from higher radius DTMs, then fill remainder with interpolation """
    from scipy.interpolate import griddata
    if len(filenames) == 0:
        raise Exception('No filenames provided!')

    filenames = sorted(filenames)
    imgs = gippy.GeoImages(filenames)
    nodata = imgs[0][0].NoDataValue()
    arr = imgs[0][0].Read()

    for i in range(1, imgs.size()):
        locs = numpy.where(arr == nodata)
        arr[locs] = imgs[i][0].Read()[locs]

    # interpolation at bad points
    goodlocs = numpy.where(arr != nodata)
    badlocs = numpy.where(arr == nodata)
    arr[badlocs] = griddata(goodlocs, arr[goodlocs], badlocs, method=interpolation)

    # write output
    imgout = gippy.GeoImage(fout, imgs[0])
    imgout.SetNoData(nodata)
    imgout[0].Write(arr)
    if shapefile is not None:
        crop2vector(imgout, gippy.GeoVector(shapefile))
    return imgout.Filename()


"""
These functions are all taken from GIPS
"""

def transform(filename, srs):
    """ Transform vector file to another SRS"""
    # TODO - move functionality into GIPPY
    bname = os.path.splitext(os.path.basename(filename))[0]
    td = tempfile.mkdtemp()
    fout = os.path.join(td, bname + '_warped.shp')
    prjfile = os.path.join(td, bname + '.prj')
    f = open(prjfile, 'w')
    f.write(srs)
    f.close()
    cmd = 'ogr2ogr %s %s -t_srs %s' % (fout, filename, prjfile)
    result = commands.getstatusoutput(cmd)
    return fout


def crop2vector(img, vector):
    """ Crop a GeoImage down to a vector """
    # transform vector to srs of image
    vecname = transform(vector.Filename(), img.Projection())
    warped_vec = gippy.GeoVector(vecname)
    # rasterize the vector
    td = tempfile.mkdtemp()
    mask = gippy.GeoImage(os.path.join(td, vector.LayerName()), img, gippy.GDT_Byte, 1)
    maskname = mask.Filename()
    mask = None
    cmd = 'gdal_rasterize -at -burn 1 -l %s %s %s' % (warped_vec.LayerName(), vecname, maskname)
    result = commands.getstatusoutput(cmd)
    mask = gippy.GeoImage(maskname)
    img.AddMask(mask[0]).Process().ClearMasks()
    mask = None
    shutil.rmtree(os.path.dirname(maskname))
    shutil.rmtree(os.path.dirname(vecname))
    return img
