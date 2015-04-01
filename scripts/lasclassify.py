#!/usr/bin/env python

import argparse
import gippy


def create_chm(dtm, dsm):
    """ Create CHM from a DTM and DSM """
    dtm_img = gippy.GeoImage(dtm)
    dsm_img = gippy.GeoImage(dsm)
    imgout = gippy.GeoImage(fout, dtm_img)
    imgout[0].Write(dsm_img[0].Read() - dtm_img[0].Read())
    return imgout


if __name__ == '__main__':
    dhf = argparse.ArgumentDefaultsHelpFormatter

    parser = argparse.ArgumentParser(description='Classify LAS file')
    parser.add_argument('fname', help='LAS file to classify')
    parser.add_argument('-s', '--slope', help='Slope', default=1.0)
    parser.add_argument('-c', '--cellsize', help='Cell Size')
