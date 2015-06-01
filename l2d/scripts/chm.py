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

import argparse
import datetime as dt
from l2d import create_chm, create_hillshade


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    desc = 'Calculate and create CHM from a DSM and DTM'
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)
    parser.add_argument('dsm', help='DSM input', default='DSM.tif', nargs='?')
    parser.add_argument('dtm', help='DTM input', default='DTM.tif', nargs='?')
    parser.add_argument('--fout', help='Output filename', default='CHM.tif')
    parser.add_argument('--hillshade', help='Generate hillshade', default=False, action='store_true')
    args = parser.parse_args()

    start = dt.datetime.now()
    print 'Creating CHM from %s and %s' % (args.dsm, args.dtm)

    fout = create_chm(args.dtm, args.dsm, args.fout)

    if args.hillshade:
        create_hillshade(fout)

    print 'Completed in %s' % (dt.datetime.now() - start)


if __name__ == "__main__":
    main()
