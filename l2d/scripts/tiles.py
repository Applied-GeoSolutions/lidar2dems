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

from glob import glob
from copy import deepcopy
from os import path, remove

from collections import OrderedDict

from l2d import get_bounding_box
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


def test(leave_shp, overwrite):
    tdir = "/mimas/projects/cmsindo/2014-lidar/results/Polygon_009_utm_50S/LAS/"
    shp = path.join(tdir, "test_tiles.shp")
    crs = deepcopy(_crs_template)
    crs['south'] = True
    lasdir2shp(tdir, shp, crs, overwrite)
    assert path.exists(shp), 'created shapefile'
    if not leave_shp:
        remove(shp)
    print('test shp: {}'.format(shp))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='lasdir2shp',
        description='Does what the name says.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-o', '--overwrite', required=False, default=False, action='store_true',
        help='overwrite existing tiles file if encountered'
    )
    parser.add_argument(
        '-s', '--shapename', required=False, default='tiles.shp',
        help='name of shapefile to be put into each directory.'
    )
    parser.add_argument(
        'top_dir',
        help=('directory to dig through for "Polygon_..." dirs. (test or '
              'test-leave-shp will run test routine')
    )
    args = parser.parse_args()

    if args.top_dir == 'test':
        test(False, args.overwrite)
    elif args.top_dir == 'test-leave-shp':
        test(True, args.overwrite)
    else:
        process_polygon_dirs(
            parentdir=args.top_dir,
            shapename=args.shapename,
            overwrite=args.overwrite,
        )
