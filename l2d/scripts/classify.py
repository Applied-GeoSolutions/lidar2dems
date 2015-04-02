#!/usr/bin/env python

"""
Calls `pdal ground` for all provided filenames and creates new las file output with parameters in output filenames
"""

import os
import argparse
from datetime import datetime


def run(filenames, slope, cellsize, outdir='./'):
    """ Run pdal ground on these files with provided arguments """
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    start0 = datetime.now()
    print 'Classifying %s files' % len(filenames)
    for i, f in enumerate(filenames):
        start = datetime.now()
        fout = os.path.join(outdir, os.path.basename(os.path.splitext(f)[0])) + '_pg_s%s_c%s.las' % (slope, cellsize)
        if not os.path.exists(fout):
            import pdb
            pdb.set_trace()
            cmd = "pdal ground -i %s -o %s --slope %s --cellSize %s --classify" % (f, fout, slope, cellsize)
            os.system(cmd)
            print 'Classified (%s of %s) %s in %s' % (i + 1, len(filenames), f, datetime.now() - start)
    print 'Completed in %s' % (datetime.now() - start0)


def main():
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file(s)', formatter_class=dhf)
    parser.add_argument('fnames', help='LAS file(s) to classify', nargs='+')
    parser.add_argument('-s', '--slope', help='Slope', default=1.0)
    parser.add_argument('-c', '--cellsize', help='Cell Size', default=3.0)
    parser.add_argument('--outdir', help='Output directory location', default='./')

    args = parser.parse_args()

    run(args.fnames, args.slope, args.cellsize, args.outdir)


if __name__ == '__main__':
    main()
