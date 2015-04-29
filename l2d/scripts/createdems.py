#!/usr/bin/env python

"""
This script processes LAS file(s) and creates a DSM and series of DTM's using different radii when gridding
LAS files will be merged together as a single point cloud for processing
"""

import argparse
from datetime import datetime
from l2d import create_dems, check_boundaries, check_overlap
import gippy, ogr
from math import floor, ceil


def main():
    """ Main function for argument parsing """
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Create DEMs from a LAS lidar file', formatter_class=dhf)
    parser.add_argument('filenames', help='Classified LAS file(s) to process', nargs='+')
    parser.add_argument('--dsm', help='Create DSM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--dtm', help='Create DTM (run for each provided radius)', nargs='*', default=[])
    parser.add_argument('--epsg', help='EPSG code to assign to DEM outputs')
    parser.add_argument('--outliers', help='Filter outliers with this StdDev threshold in the DSM', default=3.0)
    # h = 'Bounds (xmin ymin xmax ymax) of output files (VRTs)'
    # parser.add_argument('--bounds', help=h, default=None, nargs=4, type=float)
    parser.add_argument('-s', '--shapefile', help='Shapefile with bounds', default=None)
    parser.add_argument('--tileindex', help='Shapefile of LAS tile extents in polygon', default=None)
    parser.add_argument('--outdir', help='Output directory', default='./')
    args = parser.parse_args()

    start = datetime.now()

    # get bounds from shapefile
    if args.shapefile and args.tileindex is not None:
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        sites = driver.Open(args.shapefile)
        lyr = sites.GetLayer()
        tiles = driver.Open(args.tileindex)
        site_no = len(lyr)
        site_ct = 0
        
        for ftr in lyr:
        
            site_ct += 1
            filenames = check_overlap(ftr, tiles)
            bounds = create_bounds_file(ftr) # creates tmp shapefile with only the current ftr to use for gdalwarp clip boundary
            partname = '%s_of_%s' %(str(site_ct),str(site_no)) # this is to add to a naming scheme so DTMs and DSMs don't get overwritten
            
            numfiles = len(filenames)
            print 'Processing %s LAS files into DEMs' % numfiles
            classify_las(filenames) # this will be the function that classifies the files prior to creating dems - might want to add if statement in case classified files exist
            create_dems(filenames, args.dsm, args.dtm, epsg=args.epsg,
                        bounds=bounds, outliers=args.outliers, outdir=args.outdir, appendname=partname)
            print 'Processed in %s' % (datetime.now() - start)
            
            delete_bounds_file() # delete tmp shapefile

        extent = gippy.GeoVector(args.shapefile).Extent()
        bounds = [floor(extent.x0()), floor(extent.y0()), ceil(extent.x1()), ceil(extent.y1())]            


        process_dems(inputdir, outputdir, interp) # this could be called from a function in lidar2dems or we could call processdems.py separately. averaging overlapping regions?
        
    else if args.shapefile is None:
      
        print "No multi-polygon processing shapefile provided!"
    
    else if args.tileindex is None:
      
        print "No tile index shapefile provided!"


if __name__ == "__main__":
    main()
