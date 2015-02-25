#!/usr/bin/env python

import argparse

import gippy
from shapely.wkt import loads



def 
	wkt = 
	loads()




def main():
	dhf = argparse.ArgumentDefaultsHelpFormatter

	parser.add_argument('shapefile', help='Read in shapefile and loop through features')

	args = parser.parse_args()

	shp = gippy.GeoVector(args.shapefile)

	for f in range(0, shp.NumFeatures()):
		f = shp[f]
		geom = loads(f.WKT())
		print geom


if __main__ == '__main__':
	main()