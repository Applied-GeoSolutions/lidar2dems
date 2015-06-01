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

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
import glob
from datetime import datetime
from l2d import find_lasfiles, classify
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('lasdir', help='Directory of LAS file(s) to classify')
    parser.add_argument('-s', '--site', help='Polygon(s) to process', default=None)
    parser.add_argument('--slope', help='Slope (override)', default=None)
    parser.add_argument('--cellsize', help='Cell Size (override)', default=None)
    parser.add_argument('--outdir', help='Output directory location', default='./')
    h = 'Decimate the points (steps between points, 1 is no pruning'
    parser.add_argument('--decimation', help=h, default=None)
    parser.add_argument('-v', '--verbose', help='Print additional info', default=False, action='store_true')

    args = parser.parse_args()

    start = datetime.now()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    if args.site is not None:
        site = gippy.GeoVector(args.site)
    else:
        site = [None]

    fouts = []
    for feature in site:
        filenames = find_lasfiles(args.lasdir, site=feature, checkoverlap=True)
        fout = classify(filenames, site=feature, decimation=args.decimation, 
                        slope=args.slope, cellsize=args.cellsize,
                        outdir=args.outdir, verbose=args.verbose)
        fouts.append(fout)

    print 'Completed in %s' % (datetime.now() - start)


if __name__ == '__main__':
    main()
