#!/usr/bin/env python

import os
import argparse
from datetime import datetime


if __name__ == '__main__':
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file')
    parser.add_argument('fnames', help='LAS file(s) to classify')
    parser.add_argument('-s', '--slope', help='Slope', default=1.0)
    parser.add_argument('-c', '--cellsize', help='Cell Size')

    args = parser.parse_args()

    print 'Processing %s las files' % len(args.fnames)

    for fname in args.fnames:
        start = datetime.now()
        fout = os.path.splitext(fname)[0] + 'pg_s%s_c%s' % (args.slope, args.cellsize)
        if not os.path.exists(fout):
            cmd = "pdal ground -i %s --slope %s --cellSize %s --classify" % (fout, args.slope, args.cellsize)
            print cmd
            os.system(cmd)
            print 'Completed in %s' % datetime.now() - start
