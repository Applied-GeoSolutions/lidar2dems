#!/usr/bin/env python
################################################################################
#   lidar2dems - utilties for creating DEMs from LiDAR data
#
#   AUTHOR: Matthew Hanson, matt.a.hanson@gmail.com
#
#   Copyright (C) 2015 Applied Geosolutions LLC, oss@appliedgeosolutions.com
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

# Utilities mostly for interfacing with file system and settings


import os
import sys
import glob
from .vectors import check_overlap, get_vector_bounds


def dem_products(demtype):
    """ Return products for this dem type """
    products = {
        'density': ['den'],
        'dsm': ['den', 'max'],
        'dtm': ['den', 'min', 'max', 'idw']
    }
    return products[demtype]


def splitexts(filename):
    """ Split off two extensions """
    bname, ext = os.path.splitext(filename)
    parts = os.path.splitext(bname)
    if len(parts) == 2 and parts[1] in ['.den', '.min', '.max', '.mean', '.idw']:
        bname = parts[0]
        ext = parts[1] + ext
    return bname, ext


def class_params(feature, slope=None, cellsize=None):
    """ Get classification parameters based on land classification """
    try:
        # TODO - read in from config file ?
        params = {
            '1': (1, 3),    # non-forest, flat
            '2': (1, 2),    # forest, flat
            '3': (5, 2),    # non-forest, complex
            '4': (10, 2),   # forest, complex
        }
        return params[feature['class']]
    except:
        if slope is None:
            slope = '1'
        if cellsize is None:
            cellsize = '3'
    return (slope, cellsize)


def class_suffix(slope, cellsize, suffix=''):
    """" Generate LAS classification suffix """
    return '%sl2d_s%sc%s.las' % (suffix, slope, cellsize)


def find_lasfiles(lasdir='', site=None, checkoverlap=False):
    """" Find lasfiles intersecting with site """
    filenames = glob.glob(os.path.join(lasdir, '*.las'))
    if checkoverlap and site is not None:
        filenames = check_overlap(filenames, site)
    return filenames


def find_lasfile(lasdir='', site=None, params=('1', '3')):
    """ Locate LAS files within vector or given and/or matching classification parameters """
    bname = '' if site is None else site.Basename() + '_'
    pattern = bname + '_' + class_suffix(params[0], params[1])
    filenames = glob.glob(os.path.join(lasdir, pattern))
    return filenames


""" GDAL Utility wrappers """


def create_vrt(filenames, fout, site=[None], overwrite=False, verbose=False):
    """ Combine filenames into single file and align if given site """
    if os.path.exists(fout) and not overwrite:
        return fout
    cmd = [
        'gdalbuildvrt',
    ]
    if not verbose:
        cmd.append('-q')
    if site[0] is not None:
        bounds = get_vector_bounds(site)
        cmd.append('-te %s' % (' '.join(map(str, bounds))))
    cmd.append(fout)
    cmd = cmd + filenames
    if verbose:
        print 'Combining %s files into %s' % (len(filenames), fout)
    # print ' '.join(cmd)
    # subprocess.check_output(cmd)
    os.system(' '.join(cmd))
    return fout


def create_hillshade(filename):
    """ Create hillshade image from this file """
    fout = os.path.splitext(filename)[0] + '_hillshade.tif'
    sys.stdout.write('Creating hillshade: ')
    sys.stdout.flush()
    cmd = 'gdaldem hillshade %s %s' % (filename, fout)
    os.system(cmd)
    return fout
