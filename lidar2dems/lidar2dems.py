#!/usr/bin/env python

# Library functions for creating DEMs from Lidar data

import os
from lxml import etree
import tempfile
import gippy
import numpy


def create_dtm(fname, radius, epsg, bounds=None, outdir=''):
    """ Create DTM from las file """
    if outdir == '':
        bname = '%s_DTM_r%s' % (os.path.splitext(fname)[0], radius)
    else:
        bname = os.path.join(os.path.abspath(outdir), '%s_DTM_r%s' % (os.path.basename(os.path.splitext(fname)[0]), radius))

    xml = base_xml(bname, ['den', 'min', 'idw'], radius, epsg, bounds)

    # add ground point filter
    filterxml = etree.SubElement(xml[0], "Filter", type="filters.range")
    tmpxml = etree.SubElement(filterxml, "Option", name="dimension")
    tmpxml.text = "Classification"
    tmpxml = etree.SubElement(tmpxml, "Options")
    etree.SubElement(tmpxml, "Option", name="equals").text = "2"

    # las reader
    txml = etree.SubElement(filterxml, "Reader", type="readers.las")
    etree.SubElement(txml, "Option", name="filename").text = fname

    run_pipeline(xml)
    return bname


def create_dsm(fname, radius, epsg, bounds=None, outliers=None, outdir=''):
    """ Create DSM from las file """
    if outdir == '':
        bname = '%s_DSM_r%s' % (os.path.splitext(fname)[0], radius)
    else:
        bname = os.path.join(os.path.abspath(outdir), '%s_DSM_r%s' % (os.path.basename(os.path.splitext(fname)[0]), radius))

    xml = base_xml(bname, ['den', 'max'], radius, epsg, bounds)

    # add statistical outlier filter
    if outliers is not None:
        fname = create_outlier_filter(thresh=outliers)
        fxml = etree.SubElement(xml[0], "Filter", type="filters.pclblock")
        etree.SubElement(fxml, "Option", name="filename").text = fname
        txml = fxml
    else:
        # if no filter, reader needs to be child of writer block
        txml = xml[0]

    # range filter - don't include ground points
    filterxml = etree.SubElement(txml, "Filter", type="filters.range")
    tmpxml = etree.SubElement(filterxml, "Option", name="dimension")
    tmpxml.text = "Classification"
    tmpxml = etree.SubElement(tmpxml, "Options")
    etree.SubElement(tmpxml, "Option", name="max").text = "1"

    # las reader
    txml = etree.SubElement(filterxml, "Reader", type="readers.las")
    etree.SubElement(txml, "Option", name="filename").text = fname

    run_pipeline(xml)
    return bname


def create_dems(fname, dsmrad, dtmrad, epsg, bounds, outdir=''):
    """ Create all DEMS from this output """
    for rad in dtmrad:
        create_dtm(fname, rad, epsg, bounds, outdir=outdir)
    for rad in dsmrad:
        create_dsm(fname, rad, epsg, bounds, outliers=3.0, outdir=outdir)


def base_xml(fout, output, radius, epsg, bounds=None):
    """ Create initial XML for PDAL pipeline """
    xml = etree.Element("Pipeline", version="1.0")
    etree.SubElement(xml, "Writer", type="writers.p2g")
    etree.SubElement(xml[0], "Option", name="grid_dist_x").text = "1.0"
    etree.SubElement(xml[0], "Option", name="grid_dist_y").text = "1.0"
    etree.SubElement(xml[0], "Option", name="radius").text = str(radius)
    etree.SubElement(xml[0], "Option", name="output_format").text = "tif"
    etree.SubElement(xml[0], "Option", name="spatialreference").text = 'EPSG:%s' % epsg
    if bounds is not None:
        etree.SubElement(xml[0], "Option", name="bounds").text = bounds
    etree.SubElement(xml[0], "Option", name="filename").text = fout
    for t in output:
        etree.SubElement(xml[0], "Option", name="output_type").text = t
    return xml


def create_outlier_filter(meank=20, thresh=3.0):
    """ Create JSON file for performing outlier removal """
    j1 = '{"pipeline": {"name": "Outlier Removal","version": 1.0,"filters":'
    json = j1 + '[{"name": "StatisticalOutlierRemoval","setMeanK": %s,"setStddevMulThresh": %s}]}}' % (meank, thresh)
    f, fname = tempfile.mkstemp(suffix='.json')
    os.write(f, json)
    os.close(f)
    return fname


def run_pipeline(xml):
    """ Run PDAL Pipeline with provided XML """
    # print etree.tostring(xml, pretty_print=True)

    # write to temp file
    f, xmlfile = tempfile.mkstemp(suffix='.xml')
    os.write(f, etree.tostring(xml))
    os.close(f)

    cmd = [
        'pdal',
        'pipeline',
        '-i %s' % xmlfile,
    ]
    out = os.system(' '.join(cmd) + ' 2> /dev/null ')
    os.remove(xmlfile)


def create_chm(dtm, dsm):
    """ Create CHM from a DTM and DSM """
    dtm_img = gippy.GeoImage(dtm)
    dsm_img = gippy.GeoImage(dsm)
    imgout = gippy.GeoImage(fout, dtm_img)
    imgout[0].Write(dsm_img[0].Read() - dtm_img[0].Read())
    return imgout


def create_vrts(path):
    """ Create VRT for all these tiles / files """
    import re
    import glob
    pattern = re.compile('.*_(D[ST]M_.*).tif')
    fnames = glob.glob(os.path.join(path, '*.tif'))
    names = set(map(lambda x: pattern.match(x).groups()[0], fnames))
    for n in names:
        fout = os.path.abspath(os.path.join(path, '../', '%s.vrt' % n))
        if os.path.exists(fout):
            continue
        files = glob.glob(os.path.abspath(os.path.join(path, '*%s.tif' % n)))
        cmd = [
            'gdalbuildvrt',
            fout,
        ]
        cmd.extend(files)
        print 'Creating VRT %s' % fout
        os.system(' '.join(cmd))
        print 'Adding overviews'
        os.system('gdaladdo -ro %s 2 4 8 16' % fout)
        # out = os.system(' '.join(cmd) + ' 2> /dev/null ')


def gap_fill(filenames, fout, interpolation='nearest'):
    """ Gap fill from higher radius DTMs, then fill remainder with interpolation """
    from scipy.interpolate import griddata

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
    return imgout
