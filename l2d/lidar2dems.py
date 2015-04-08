#!/usr/bin/env python

# Library functions for creating DEMs from Lidar data

import os
from lxml import etree
import tempfile
import gippy
import numpy


def xml_base(fout, output, radius, epsg, bounds=None):
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


def xml_add_pclblock(xml, pclblock):
    """ Add pclblock Filter element by taking in filename of a JSON file """
    _xml = etree.SubElement(xml, "Filter", type="filters.pclblock")
    etree.SubElement(_xml, "Option", name="filename").text = pclblock
    return _xml


def xml_add_outlier_filter(xml, meank=20, thresh=3.0):
    """ Add outlier Filter element and return """
    # create JSON file for performing outlier removal
    j1 = '{"pipeline": {"name": "Outlier Removal","version": 1.0,"filters":'
    json = j1 + '[{"name": "StatisticalOutlierRemoval","setMeanK": %s,"setStddevMulThresh": %s}]}}' % (meank, thresh)
    f, fname = tempfile.mkstemp(suffix='.json')
    os.write(f, json)
    os.close(f)
    return xml_add_pclblock(xml, f)


def xml_add_classification_filter(xml, classification, equality="equals"):
    """ Add classification Filter element and return """
    fxml = etree.SubElement(xml, "Filter", type="filters.range")
    _xml = etree.SubElement(fxml, "Option", name="dimension")
    _xml.text = "Classification"
    _xml = etree.SubElement(_xml, "Options")
    etree.SubElement(_xml, "Option", name=equality).text = str(classification)
    return fxml


def xml_add_reader(xml, filename):
    """ Add LAS Reader Element and return """
    _xml = etree.SubElement(xml, "Reader", type="readers.las")
    etree.SubElement(_xml, "Option", name="filename").text = os.path.abspath(filename)
    return _xml


def xml_add_readers(xml, filenames):
    """ Add merge Filter element and readers to a Writer element and return Filter element """
    if len(filenames) > 1:
        fxml = etree.SubElement(xml, "Filter", type="filters.merge")
    else:
        fxml = xml
    for f in filenames:
        xml_add_reader(fxml, f)
    return fxml


def run_pipeline(xml):
    """ Run PDAL Pipeline with provided XML """
    xml_print(xml)

    # write to temp file
    f, xmlfile = tempfile.mkstemp(suffix='.xml')
    os.write(f, etree.tostring(xml))
    os.close(f)

    cmd = [
        'pdal',
        'pipeline',
        '-i %s' % xmlfile,
    ]
    #out = os.system(' '.join(cmd) + ' 2> /dev/null ')
    out = os.system(' '.join(cmd))
    os.remove(xmlfile)


def xml_print(xml):
    """ Pretty print xml """
    print etree.tostring(xml, pretty_print=True)


def create_dtm(filenames, radius, epsg, bounds=None, outdir=''):
    """ Create DTM from las file """
    bname = os.path.join(os.path.abspath(outdir), 'DTM_r%s' % radius)

    xml = xml_base(bname, ['den', 'min', 'idw'], radius, epsg, bounds)
    fxml = xml_add_classification_filter(xml[0], 2)
    xml_add_readers(fxml, filenames)

    run_pipeline(xml)
    return bname


def create_dsm(filenames, radius, epsg, bounds=None, outliers=None, outdir=''):
    """ Create DSM from las file """
    bname = os.path.join(os.path.abspath(outdir), 'DSM_r%s' % radius)

    xml = xml_base(bname, ['den', 'max'], radius, epsg, bounds)
    # add statistical outlier filter
    if outliers is not None:
        _xml = xml_add_outlier_filter(xml[0], thresh=outliers)
    else:
        _xml = xml[0]
    # do not include ground points
    fxml = xml_add_classification_filter(_xml, 1, equality="max")
    xml_add_readers(fxml, filenames)

    run_pipeline(xml)
    return bname


def create_dems(filenames, dsmrad, dtmrad, epsg, bounds=None, outdir=''):
    """ Create all DEMS from this output """
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for rad in dtmrad:
        create_dtm(filenames, rad, epsg, bounds, outdir=outdir)
    for rad in dsmrad:
        create_dsm(filenames, rad, epsg, bounds, outliers=3.0, outdir=outdir)


def create_chm(dtm, dsm, chm):
    """ Create CHM from a DTM and DSM """
    dtm_img = gippy.GeoImage(dtm)
    dsm_img = gippy.GeoImage(dsm)
    imgout = gippy.GeoImage(chm, dtm_img)
    imgout[0].Write(dsm_img[0].Read() - dtm_img[0].Read())
    return imgout.Filename()


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


def gap_fill(filenames, fout, interpolation='nearest'):
    """ Gap fill from higher radius DTMs, then fill remainder with interpolation """
    from scipy.interpolate import griddata

    gippy.Options.SetVerbose(4)

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
    return imgout.Filename()
