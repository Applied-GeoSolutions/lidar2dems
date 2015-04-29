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
from datetime import datetime
from math import floor, ceil


def _xml_base(fout, output, radius, srs):  # , bounds=None):
    """ Create initial XML for PDAL pipeline containing a Writer element """
    xml = etree.Element("Pipeline", version="1.0")
    etree.SubElement(xml, "Writer", type="writers.p2g")
    etree.SubElement(xml[0], "Option", name="grid_dist_x").text = "1.0"
    etree.SubElement(xml[0], "Option", name="grid_dist_y").text = "1.0"
    etree.SubElement(xml[0], "Option", name="radius").text = str(radius)
    etree.SubElement(xml[0], "Option", name="output_format").text = "tif"
    etree.SubElement(xml[0], "Option", name="spatialreference").text = srs  #'EPSG:%s' % epsg
    # this not yet working in p2g
    # if bounds is not None:
    #    etree.SubElement(xml[0], "Option", name="bounds").text = bounds
    etree.SubElement(xml[0], "Option", name="filename").text = fout
    for t in output:
        etree.SubElement(xml[0], "Option", name="output_type").text = t
    return xml


def _xml_add_pclblock(xml, pclblock):
    """ Add pclblock Filter element by taking in filename of a JSON file """
    _xml = etree.SubElement(xml, "Filter", type="filters.pclblock")
    etree.SubElement(_xml, "Option", name="filename").text = pclblock
    return _xml


def _xml_add_outlier_filter(xml, meank=20, thresh=3.0):
    """ Add outlier Filter element and return """
    # create JSON file for performing outlier removal
    j1 = '{"pipeline": {"name": "Outlier Removal","version": 1.0,"filters":'
    json = j1 + '[{"name": "StatisticalOutlierRemoval","setMeanK": %s,"setStddevMulThresh": %s}]}}' % (meank, thresh)
    f, fname = tempfile.mkstemp(suffix='.json')
    os.write(f, json)
    os.close(f)
    return _xml_add_pclblock(xml, fname)


def _xml_add_classification_filter(xml, classification, equality="equals"):
    """ Add classification Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "Classification"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name=equality).text = str(classification)
    return fxml


def _xml_add_scanangle_filter(xml, maxabsangle):
    """ Add scan angle Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "ScanAngleRank"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name="max").text = maxabsangle
    etree.SubElement(_xml, "Option", name="min").text = -maxabsangle
    return fxml


def _xml_add_scanedge_filter(xml):
    """ Add EdgeOfFlightLine Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "EdgeOfFlightLine"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name="equals").text = 0
    return fxml


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


def run_pipeline(xml):
    """ Run PDAL Pipeline with provided XML """
    # _xml_print(xml)

    # write to temp file
    f, xmlfile = tempfile.mkstemp(suffix='.xml')
    os.write(f, etree.tostring(xml))
    os.close(f)

    cmd = [
        'pdal',
        'pipeline',
        '-i %s' % xmlfile,
        '-v4',
    ]
    out = os.system(' '.join(cmd) + ' 2> /dev/null ')
    # out = os.system(' '.join(cmd))
    os.remove(xmlfile)


def _xml_print(xml):
    """ Pretty print xml """
    print etree.tostring(xml, pretty_print=True)


def create_dsm(filenames, radius, vector, outliers=None, maxangle=None, outputs=None, outdir=''):
    """ Create DSM from LAS file(s) """
    demtype = 'DSM'
    start = datetime.now()
    bname = os.path.join(os.path.abspath(outdir), '%s_r%s' % (demtype, radius))
    print 'Creating %s: %s' % (demtype, bname)

    if outputs is None:
        outputs = ['den', 'max']

    xml = _xml_base(bname, outputs, radius, vector.Projection())  # , bounds)
    _xml = xml[0]

    # filter statistical outliers
    if outliers is not None:
        _xml = _xml_add_outlier_filter(xml[0], thresh=outliers)

    if maxangle is not None:
        _xml = _xml_add_scanangle_filter(xml[0], maxangle)

    # non-ground points only
    fxml = _xml_add_classification_filter(_xml, 1, equality='max')

    _xml_add_readers(fxml, filenames)

    run_pipeline(xml)

    if vector is not None:
        warp_image('%s.%s.tif' % (bname, outputs[-1]), vector)

    print 'Created %s in %s' % (bname, datetime.now() - start)
    return bname


def create_dtm(filenames, radius, vector, outputs=None, outdir=''):
    """ Create DTM from LAS file(s) """
    demtype = 'DTM'
    start = datetime.now()
    bname = os.path.join(os.path.abspath(outdir), '%s_r%s' % (demtype, radius))
    print 'Creating %s: %s' % (demtype, bname)

    if outputs is None:
        outputs = ['den', 'min', 'idw']

    xml = _xml_base(bname, outputs, radius, vector.Projection())  # , bounds)

    # ground points only
    fxml = _xml_add_classification_filter(xml[0], 2)

    _xml_add_readers(fxml, filenames)

    run_pipeline(xml)

    if vector is not None:
        warp_image('%s.%s.tif' % (bname, outputs[-1]), vector)

    print 'Created %s in %s' % (bname, datetime.now() - start)
    return bname


def create_dem(filenames, demtype, radius, epsg, bounds=None, outliers=None, outdir='', outputs=None):
    """ Create DEM from LAS file """
    start = datetime.now()
    bname = os.path.join(os.path.abspath(outdir), '%s_r%s' % (demtype, radius))
    print 'Creating %s: %s' % (demtype, bname)

    if outputs is None:
        if demtype == 'DSM':
            outputs = ['den', 'max']
        else:  # DTM
            outputs = ['den', 'min', 'idw']

    xml = _xml_base(bname, outputs, radius, epsg)  # , bounds)
    if demtype == 'DSM':
        if outliers is not None:
            _xml = _xml_add_outlier_filter(xml[0], thresh=outliers)
        else:
            _xml = xml[0]
        fxml = _xml_add_classification_filter(_xml, 1, equality='max')
    else:  # DTM
        fxml = _xml_add_classification_filter(xml[0], 2)
    _xml_add_readers(fxml, filenames)

    run_pipeline(xml)

    warp_image('%s.%s.tif' % (bname, outputs[-1]), bounds)

    print 'Created %s in %s' % (bname, datetime.now() - start)
    return bname


def create_hillshade(filename):
    """ Create hillshade image from this file """
    fout = os.path.splitext(filename)[0] + '_hillshade.tif'
    sys.stdout.write('Creating hillshade: ')
    sys.stdout.flush()
    cmd = 'gdaldem hillshade %s %s' % (filename, fout)
    os.system(cmd)
    return fout


def create_density_image(filenames, epsg, outdir='./'):
    """ Create density image using all points """
    start = datetime.now()
    bname = os.path.join(os.path.abspath(outdir), 'allpoints')
    exist = glob.glob(bname + '*')
    if len(exist) > 0:
        return bname

    print 'Creating %s' % bname

    xml = _xml_base(bname, ['den'], 0.56, epsg)
    _xml_add_readers(xml[0], filenames)

    run_pipeline(xml)

    print 'Created %s in %s' % (bname, datetime.now() - start)
    return bname


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
        sys.stdout.write('Warping and clipping image: ')
    else:
        sys.stdout.write('Warping image: ')
    sys.stdout.flush()
    out = os.system(' '.join(cmd))
    if clip:
        img = gippy.GeoImage(fout, True)
        crop2vector(img, vector)
    return fout


def create_dems(filenames, dsmrad, dtmrad, epsg, bounds=None, outliers=3.0, outdir=''):
    """ Create all DEMS from this output """
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for rad in dsmrad:
        create_dem(filenames, 'DSM', rad, epsg, bounds, outliers=outliers, outdir=outdir)
    for rad in dtmrad:
        create_dem(filenames, 'DTM', rad, epsg, bounds, outdir=outdir)


def create_dems2(filenames, dsmrad, dtmrad, vector, outliers=2.0, maxangle=None, outdir=''):
    """ Create series of DEMs, both DSM and DTM """
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for rad in dsmrad:
        create_dsm(filenames, rad, vector, outliers=outliers, outdir=outdir)
    for rad in dtmrad:
        create_dtm(filenames, rad, vector, outdir=outdir)


def get_meta_data(lasfilename):
    cmd = ['pdal', 'info', '--metadata', '--input', os.path.abspath(lasfilename)]
    meta = json.loads(subprocess.check_output(cmd))['metadata'][0]
    return meta


def check_boundaries(filenames, vector):
    """ Check that each file at least partially falls within bounds """
    bounds = get_vector_bounds(vector)
    goodf = []
    for f in filenames:
        meta = get_meta_data(f)
        if (meta['minx'] < bounds[2]) and (meta['maxx'] > bounds[0]) and (meta['miny'] < bounds[3]) and (meta['maxy'] > bounds[1]):
            goodf.append(f)
        else:
            pass
            # print 'Image %s out of bounds: %s %s %s %s' % (f, meta['minx'], meta['miny'], meta['maxx'], meta['maxy'])
    return goodf


def get_bounding_box(filename, min_points=2):
    """ Get bounding box from LAS file """
    meta = get_meta_data(filename)
    mx, my, Mx, My = meta['minx'], meta['miny'], meta['maxx'], meta['maxy']
    if meta['count'] < min_points:
        raise Exception('{} contains only {} points (min_points={}).'
                        .format(filename, meta['count'], min_points))
    bounds = [(mx, my), (Mx, my), (Mx, My), (mx, My), (mx, my)]
    return bounds


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

import commands
import shutil


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
