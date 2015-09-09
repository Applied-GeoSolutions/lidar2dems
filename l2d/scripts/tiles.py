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
from glob import glob
from copy import deepcopy
from os import path, remove
from datetime import datetime
from collections import OrderedDict

from l2d.geo import get_bounding_box, Vector
from fiona import collection

_polygon_template = {
    'geometry': {
        'coordinates': [],  # list of lists of points defining box
        'type': 'Polygon'
    },
    'id': '0',
    'properties': OrderedDict([(u'las_file', u'')]),
    'type': 'Feature'
}

_crs_template = {
    u'datum': u'WGS84',
    u'no_defs': True,
    u'proj': u'utm',
    u'units': u'm',
    u'zone': 50
}

_polygon_file_schema = {
    'geometry': 'Polygon',
    'properties': OrderedDict([(u'las_file', 'str')])
}


def lasdir2shp(lasdir, fout, crs, overwrite=False):
    '''
    Map each file in the lasdir to a polygon in the shapefile fout.
    '''
    if path.exists(fout):
        if overwrite:
            remove(fout)
        else:
            print('Output file {} already exists.  Skipping...'.format(fout))
            return

    filenames = glob(path.join(lasdir, '*.las'))
    oschema = _polygon_file_schema.copy()
    poly = deepcopy(_polygon_template)

    with collection(
            fout, 'w', crs=crs, driver="ESRI Shapefile", schema=oschema
        ) as oshp:
        for filename in filenames:
            try:
                poly['geometry']['coordinates'] = [get_bounding_box(filename)]
            except Exception as e:
                if 'min_points' in str(e):
                    continue
                raise e
            poly['properties']['las_file'] = filename
            oshp.write(poly)
            poly['id'] = str(int(poly['id']) + 1)


def process_polygon_dirs(parentdir, shapename, overwrite=False,):
    '''
    Find all directories in parentdir, and create a polygon shapefile in each
    directory using lasdir2shp.
    '''
    params = sorted(
        map(
            lambda x: [x] + x.split('_')[1:4:2],
            glob(path.join(parentdir, 'Polygon_???_utm_???'))
        ),
        key=lambda y: y[1],
    )

    for poly_dir, poly_id, utmzone in params:
        print poly_dir, poly_id, utmzone
        crs = deepcopy(_crs_template)
        if utmzone.endswith('S'):
            crs['south'] = True
        crs['zone'] = utmzone[:-1]
        lasdir2shp(
            path.join(poly_dir, 'LAS'),
            path.join(poly_dir, 'tiles.shp'),
            crs,
            overwrite,
        )


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create shapefile showing bounds of LAS files', formatter_class=dhf)
    parser.add_argument('files', help="List of input LiDAR files")
    parser.add_argument(
        '-s', '--shapefile', required=False, default='tiles.shp',
        help='Name of output shapefile')
    parser.add_argument(
        '-o', '--overwrite', required=False, default=False, action='store_true',
        help='Overwrite existing output shapefile')
    parser.add_argument(
        '-epsg', default=4326,
        help='EPSG code of LiDAR spatial reference system')
    parser.add_argument(
        '-v', '--verbose', default=False, action='store_true',
        help='Print additional info')

    # args = parser.parse_args()

    # start = datetime.now()

    print 'l2d_tiles not yet implemented'

    # print 'Completed in %s' % (datetime.now() - start)


if __name__ == '__main__':
    main()
