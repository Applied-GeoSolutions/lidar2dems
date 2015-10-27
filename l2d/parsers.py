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

import argparse
import sys


class l2dParser(argparse.ArgumentParser):
    """ Extends argparser parser """

    demtypes = {
        'density': 'Total point density with optional filters',
        'dsm': 'Digital Surface Model (non-ground points)',
        'dtm': 'Digital Terrain Model (ground points)'
    }

    def __init__(self, commands=False, **kwargs):
        super(l2dParser, self).__init__(**kwargs)
        self.commands = commands
        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter
        self.parent_parsers = []

    def error(self, message):
        """ print help on error """
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

    def get_parser(self):
        """ Get new parser if using commands otherwise return self """
        if self.commands:
            return l2dParser(add_help=False)
        else:
            return self

    def parse_args(self, **kwargs):
        if self.commands:
            subparser = self.add_subparsers(dest='demtype')
            for src, desc in self.demtypes.items():
                subparser.add_parser(src, help=desc, parents=self.parent_parsers)
        args = super(l2dParser, self).parse_args(**kwargs)
        return args

    def add_input_parser(self):
        """ Add input arguments to parser """
        parser = self.get_parser()
        group = parser.add_argument_group('input options')
        group.add_argument('lasdir', help='Directory of LAS file(s) to process')
	group.add_argument(
	    '--vendor_classified', 
	    help='Files are not classified by l2d, the l2d naming scheme was not used for classified files', default=False)
    	group.add_argument('--slope', help='Slope (override)', default=None)
    	group.add_argument('--cellsize', help='Cell Size (override)', default=None)
        group.add_argument('-r', '--radius', help='Create DEM or each provided radius', nargs='*', default=['0.56'])
        group.add_argument('-s', '--site', help='Shapefile of site(s) in same projection as LiDAR', default=None)
        group.add_argument('-v', '--verbose', help='Print additional info', default=False, action='store_true')
        self.parent_parsers.append(parser)

    def add_output_parser(self):
        parser = self.get_parser()
        group = parser.add_argument_group('output options')
        group.add_argument('--outdir', help='Output directory', default='./')
        group.add_argument('--suffix', help='Suffix to append to output', default='')
        group.add_argument(
            '-g', '--gapfill', default=False, action='store_true',
            help='Gapfill using multiple radii products and interpolation (no effect on density products)')
        group.add_argument(
            '-o', '--overwrite', default=False, action='store_true',
            help='Overwrite any existing output files')
        self.parent_parsers.append(parser)

    def add_filter_parser(self):
        """ Add a few different filter options to the parser """
        parser = self.get_parser()
        group = parser.add_argument_group('filtering options')
        group.add_argument('--maxsd', help='Filter outliers with this SD threshold', default=None)
        group.add_argument('--maxangle', help='Filter by maximum absolute scan angle', default=None)
        group.add_argument('--maxz', help='Filter by maximum elevation value', default=None)
        # group.add_argument('--scanedge', help='Filter by scanedge value (0 or 1)', default=None)
        group.add_argument('--returnnum', help='Filter by return number', default=None)
        h = 'Decimate the points (steps between points, 1 is no pruning'
        group.add_argument('--decimation', help=h, default=None)
        self.parent_parsers.append(parser)
