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
Create Canopy Height model from a DSM and DTM
"""

import os
import argparse
import datetime as dt
from l2d.utils import create_chm, create_hillshade, create_vrt
import gippy


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Calculate and create CHM from a DSM and DTM'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument(
        'demdir', help='Directory holding DEMs (and used to store CHM output')
    parser.add_argument(
        '-s', '--site', default=None,
        help='Site shapefile name (use if used for DTM/DSM creation')
    parser.add_argument(
        '--dsm', default='dsm.max.tif',
        help='Filename of DSM input (will be preceded by feature name if using shapefile')
    parser.add_argument(
        '--dtm', default='dtm.idw.tif',
        help='Filename of DTM input (will be preceded by feature name if using shapefile')
    parser.add_argument(
        '--fout', default='chm.tif',
        help='Output filename (created in demdir)')
    parser.add_argument(
        '--hillshade', default=False, action='store_true',
        help='Generate hillshade')
    parser.add_argument(
        '-v', '--verbose', default=False, action='store_true',
        help='Print additional info')
    args = parser.parse_args()

    start = dt.datetime.now()
    print 'Creating CHM from DEMS in %s' % (os.path.relpath(args.demdir))

    if args.site is not None:
        site = gippy.GeoVector(args.site)
    else:
        site = [None]

    fout_final = os.path.join(args.demdir, os.path.splitext(args.fout)[0] + '.vrt')

    fouts = []
    hillfouts = []
    for feature in site:
        prefix = os.path.join(args.demdir, '' if feature is None else feature.Basename() + '_')
        fdtm = prefix + args.dtm
        fdsm = prefix + args.dsm
        if not os.path.exists(fdtm) or not os.path.exists(fdsm):
            print "No valid input files found (%s)" % prefix
            continue
        try:
            fout = create_chm(fdtm, fdsm, prefix + args.fout)
            fouts.append(fout)
        except Exception as e:
            print "Error creating %s: %s" % (fout, e)
            if args.verbose:
                import traceback
                print traceback.format_exc()

        if args.hillshade:
            hillfouts.append(create_hillshade(fout))

    # if multiple file output then combine them together
    if len(fouts) > 0 and site[0] is not None:
        create_vrt(fouts, fout_final, site=site)
        if args.hillshade:
            fout = os.path.splitext(fout_final)[0] + '_hillshade.tif'
            create_vrt(hillfouts, fout, site=site)

    print 'Completed %s in %s' % (fout_final, dt.datetime.now() - start)


if __name__ == "__main__":
    main()
