#!/usr/bin/env python

from glob import glob
import math
from copy import deepcopy
from os import walk, path, remove
from pprint import pprint

from collections import OrderedDict

import pdb

from lidar2dems import get_bounding_box
from fiona import collection

_polygon_template = {
    'geometry': {
        'coordinates': [],  # list of points defining box
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
            poly['geometry']['coordinates'] = [get_bounding_box(filename)]
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
        if utmzone.endswith('S') and 'south' in crs:
            crs['south'] = True
        crs['zone'] = utmzone[:-1]
        lasdir2shp(
            path.join(poly_dir, 'LAS'),
            path.join(poly_dir, 'tiles.shp'),
            crs,
            overwrite,
        )


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
        help=('Dir to dig through for "Polygon_..." dirs.')
    )
    args = parser.parse_args()
    process_polygon_dirs(parentdir=args.top_dir, shapename=args.shapename, overwrite=args.overwrite)

# "PG:dbname='geodata' host='congo' port='5432' user='geosolution' password='Ni28Cu29Zn30'|layername=countries"
