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

import os
import unittest
import gippy
from l2d.utils import get_classification_filename, find_lasfiles


class UtilsTest(unittest.TestCase):

    vfilename = os.path.join(os.path.dirname(__file__), 'vectors/features.shp')
    tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')
    lasdir = os.path.join(os.path.dirname(__file__), 'las')

    def setUp(self):
        """ Open vector file """
        self.features = gippy.GeoVector(self.vfilename)

    def test_classification_filename(self):
        """ Test getting classification filename """
        fname = get_classification_filename(None, outdir=self.tmpdir)
        self.assertEqual(os.path.dirname(fname), self.tmpdir)
        self.assertEqual(os.path.basename(fname)[0:4], 'l2d_')

        fname = get_classification_filename(self.features[0], outdir=self.tmpdir)
        self.assertEqual(os.path.dirname(fname), self.tmpdir)
        bname = os.path.splitext(os.path.basename(self.vfilename))[0]
        self.assertEqual(bname, bname[0:len(bname)])

    def test_find_lasfiles(self):
        """ Test finding las files """
        fnames = find_lasfiles(self.lasdir)
        self.assertTrue(len(fnames) == 4)

    def find_classified_lasfile(self):
        """ Test finding classified lasfile """
        # should some classified las be stored in repo?
        pass
