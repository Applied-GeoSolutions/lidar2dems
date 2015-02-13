#!/usr/bin/env python

import argparse
import gippy


def main():
        dhf = argparse.ArgumentDefaultsHelpFormatter

        # Top level parser
        parser = argparse.ArgumentParser(description='Subtract two images', formatter_class=dhf)
        parser.add_argument('file1', help='File 1')
        parser.add_argument('file2', help='File 2')
        parser.add_argument('fileout', help='Output filename')
        parser.add_argument('-v', '--verbose', help='Verbosity - 0: quiet, 1: normal, 2+: debug', default=1, type=int)
        args = parser.parse_args()

        gippy.Options.SetVerbose(args.verbose)

        img1 = gippy.GeoImage(args.file1)
        img2 = gippy.GeoImage(args.file2)

        imgout = gippy.GeoImage(args.fileout, img1)
        imgout[0].Write(img1[0].Read()-img2[0].Read())


if __name__ == '__main__':
    main()
