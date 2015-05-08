#!/usr/bin/env python

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
from datetime import datetime


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('filenames', help='LAS file(s) to classify', nargs='+')
    parser.add_argument('-s', '--slope', help='Slope', default=1.0)
    parser.add_argument('-c', '--cellsize', help='Cell Size', default=3.0)
    parser.add_argument('--outdir', help='Output directory location', default='./')

    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    start0 = datetime.now()
    print 'Classifying %s files' % len(args.filenames)
    for i, f in enumerate(args.filenames):
        start = datetime.now()
        suffix = '_l2d_s%sc%s.las' % (args.slope, args.cellsize)
        fout = os.path.join(args.outdir, os.path.basename(os.path.splitext(f)[0])) + suffix
        if not os.path.exists(fout):
            cmd = "pdal ground -i %s -o %s --slope %s --cellSize %s --classify" % (f, fout, args.slope, args.cellsize)
            os.system(cmd)
            print 'Classified (%s of %s) %s in %s' % (i + 1, len(args.filenames), f, datetime.now() - start)
    print 'Completed in %s' % (datetime.now() - start0)


if __name__ == '__main__':
    main()
