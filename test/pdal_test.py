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

# last modified
# Time-stamp: <2017-02-08 17:04:30 icooke on north>

import os
import shutil
import unittest
import gippy
from l2d.utils import find_lasfiles, get_classification_filename, find_classified_lasfile, \
    class_params, create_vrt, create_chm
from l2d.pdal import classify, create_dems


class PDALTest(unittest.TestCase):
    """ Test PDAL functions """

    lasdir = os.path.join(os.path.dirname(__file__), 'las')
    testdir = os.path.join(os.path.dirname(__file__), 'testdir')
    vfilename = os.path.join(os.path.dirname(__file__), 'vectors/features.shp')

    def setUp(self):
        """ Set up test environment """
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        self.features = gippy.GeoVector(self.vfilename)

    def tearDown(self):
        """ Clean up test environment """
        # shutil.rmtree(self.testdir)
        pass

    def test0_classify(self):
        """ Test classification """
        fnames = find_lasfiles(self.lasdir)
        self.assertTrue(len(fnames) == 4)
        for f in self.features:
            fout = get_classification_filename(f, self.testdir)
            slope, cellsize = class_params(f)
            classify(fnames, fout, site=f, slope=slope, cellsize=cellsize)
            fouts = find_classified_lasfile(self.testdir, site=f, params=(slope, cellsize))
            self.assertTrue(len(fouts) == 1)

    def test1_create_density(self):
        """ Test creating density """
        fouts = []
        for f in self.features:
            lasfiles = find_lasfiles(self.lasdir, site=f, checkoverlap=True)
            fout = create_dems(lasfiles, 'density', site=f, outdir=self.testdir)
            fouts.append(fout['den'])

        [self.assertTrue(os.path.exists(f)) for f in fouts]

        # create VRT
        fout = os.path.join(self.testdir, 'density.vrt')
        create_vrt(fouts, fout, site=self.features)

    def test2_create_dtm(self):
        """ Create DTM """
        pieces = []
        for f in self.features:
            lasfiles = find_classified_lasfile(self.testdir, site=f, params=class_params(f))
            pouts = create_dems(lasfiles, 'dtm', site=f, gapfill=True,
                                radius=['0.56', '1.41', '2.50'], outdir=self.testdir)
            [self.assertTrue(os.path.exists(fout) for fout in pouts.items())]
            pieces.append(pouts)

        for product in pouts.keys():
            # there will be mult if gapfill False and multiple radii....use 1st one
            fnames = [piece[product] for piece in pieces]
            fout = os.path.join(self.testdir, 'dtm-%s.vrt' % product)
            create_vrt(fnames, fout, site=self.features)
            self.assertTrue(os.path.exists(fout))

    def test3_create_dsm(self):
        """ Create DSM """
        pieces = []
        for f in self.features:
            lasfiles = find_classified_lasfile(self.testdir, site=f, params=class_params(f))
            pouts = create_dems(lasfiles, 'dsm', site=f, gapfill=True, outdir=self.testdir)
            [self.assertTrue(os.path.exists(fout) for fout in pouts.items())]
            pieces.append(pouts)

        for product in pouts.keys():
            # there will be mult if gapfill False and multiple radii....use 1st one
            fnames = [piece[product] for piece in pieces]
            fout = os.path.join(self.testdir, 'dsm-%s.vrt' % product)
            create_vrt(fnames, fout, site=self.features)
            self.assertTrue(os.path.exists(fout))

    def test4_create_chm(self):
        """ Create CHM """
        fouts = []
        for f in self.features:
            prefix = os.path.join(self.testdir, f.Basename() + '_')
            fdtm = os.path.join(self.testdir, prefix + 'dtm.idw.tif')
            fdsm = os.path.join(self.testdir, prefix + 'dsm.max.tif')
            fout = create_chm(fdtm, fdsm, prefix + 'chm.tif')
            fouts.append(fout)
            self.assertTrue(os.path.exists(fout))

        fout = create_vrt(fouts, os.path.join(self.testdir, 'chm.vrt'), site=self.features)
        self.assertTrue(os.path.exists(fout))
