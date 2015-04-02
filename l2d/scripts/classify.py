#!/usr/bin/env python

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
from datetime import datetime


if __name__ == '__main__':
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('fnames', help='LAS file(s) to classify', nargs='+')
    parser.add_argument('-s', '--slope', help='Slope', default=1.0)
    parser.add_argument('-c', '--cellsize', help='Cell Size', default=3.0)

    args = parser.parse_args()

    print 'Processing %s las files' % len(args.fnames)

    for f in args.fnames:
        start = datetime.now()
        fout = os.path.splitext(f)[0] + '_pg_s%s_c%s.las' % (args.slope, args.cellsize)
        if not os.path.exists(fout):
            cmd = "pdal ground -i %s -o %s --slope %s --cellSize %s --classify" % (f, fout, args.slope, args.cellsize)
            print cmd
            os.system(cmd)
            print 'Completed in %s' % (datetime.now() - start)
