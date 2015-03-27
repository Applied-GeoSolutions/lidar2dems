#!/usr/bin/env python

# this script processes a LAS file and creates a DTM, DSM, and CHM

import os
import sys
import argparse
import subprocess
from lxml import etree
import tempfile
from datetime import datetime


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


def run_pipeline(xml):
    """ Run PDAL Pipeline with this XML """
    #print etree.tostring(xml, pretty_print=True)
    
    # write to temp file
    f, xmlfile = tempfile.mkstemp(suffix='.xml')
    os.write(f, etree.tostring(xml))
    os.close(f)
    
    cmd = [
        'pdal',
        'pipeline',
        '-i %s' % xmlfile, 
    ]
    #cmdstr = ' '.join(cmd)
    out = os.system(' '.join(cmd) + ' 2> /dev/null ')
    os.remove(xmlfile)


def create_dtm(fname, radius, epsg, bounds=None, outdir=''):
    """ Create DTM from las file """
    if outdir == '':
        bname = '%s_DSM_r%s' % (os.path.splitext(fname)[0], radius)
    else:
        bname = os.path.join(os.path.abspath(outdir), '%s_DSM_r%s' % (os.path.basename(os.path.splitext(fname)[0]), radius))

    xml = base_xml(bname, ['den','min','idw'], radius, epsg, bounds)

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


def create_dsm(fname, radius, epsg, bounds=None, pclblock=None, outdir=''):
    """ Create DSM from las file """
    if outdir == '':
        bname = '%s_DSM_r%s' % (os.path.splitext(fname)[0], radius)
    else:
        bname = os.path.join(os.path.abspath(outdir), '%s_DSM_r%s' % (os.path.basename(os.path.splitext(fname)[0]), radius))

    xml = base_xml(bname, ['den','max'], radius, epsg, bounds)

    # add statistical outlier filter
    if pclblock is not None:
        fxml = etree.SubElement(xml[0], "Filter", type="filters.pclblock")
        etree.SubElement(fxml, "Option", name="filename").text = pclblock
        txml = fxml 
    else:
        # if no filter, reader needs to be child of writer block
        txml = xml[0]

    # las reader
    txml = etree.SubElement(txml, "Reader", type="readers.las")
    etree.SubElement(txml, "Option", name="filename").text = fname

    run_pipeline(xml)
    return bname


def create_chm(dtm, dsm):
    """ Create CHM from a DTM and DSM """
    dtm_img = gippy.GeoImage(dtm)
    dsm_img = gippy.GeoImage(dsm)
    imgout = gippy.GeoImage(fout, dtm_img)
    imgout[0].Write(dsm_img[0].Read() - dtm_img[0].Read())
    return imgout


def create_dems(fname, dsmrad, dtmrad, epsg, bounds, outdir=''):
    """ Create all DEMS from this output """
    pclblock = os.path.join(os.path.dirname(sys.argv[0]), 'outlier_filter.json')
    for rad in dtmrad:
        create_dtm(fname, rad, epsg, bounds, outdir=outdir)
    for rad in dsmrad:
        create_dsm(fname, rad, epsg, bounds, pclblock=pclblock, outdir=outdir)


if __name__ == "__main__":
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('fnames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='+', default=['0.56419'])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='+', default=['0.56419'])
    parser.add_argument('--chm', help='Create CHM from DTM and DSM', default=False, action='store_true')
    parser.add_argument('--outdir', help='Output directory', default='')
    args = parser.parse_args()

    numfiles = len(args.fnames)
    print 'Processing %s files' % numfiles

    for i, f in enumerate(args.fnames):
        start = datetime.now()

        # figure out bounds
        bname = os.path.basename(os.path.splitext(f)[0]).split('_')[0]
        b = os.path.basename(bname).split('-')
        x = float(b[0]) + 0.5
        y = float(b[1]) + 0.5
        bounds = "([%s,%s],[%s,%s])" % (x, x+499, y, y+499)
        bounds = None

        create_dems(os.path.abspath(f), args.dsm, args.dtm, args.epsg, bounds, outdir=args.outdir)
        
        print 'Processed (%s of %s) %s in %s' % (i+1, numfiles, f, datetime.now()-start)



