---
layout: page
title: "l2d_classify"
category: doc
date: 2015-05-28 22:46:23
order: 2
---

## Online Help
~~~
$ l2d_classify -h
usage: l2d_classify [-h] [-s SITE] [--slope SLOPE] [--cellsize CELLSIZE]
                    [--outdir OUTDIR] [--decimation DECIMATION] [-v]
                    lasdir

Classify LAS file(s)

positional arguments:
  lasdir                Directory of LAS file(s) to classify

optional arguments:
  -h, --help            show this help message and exit
  -s SITE, --site SITE  Polygon(s) to process (default: None)
  --slope SLOPE         Slope (override) (default: None)
  --cellsize CELLSIZE   Cell Size (override) (default: None)
  --outdir OUTDIR       Output directory location (default: ./)
  --decimation DECIMATION
                        Decimate the points (steps between points, 1 is no
                        pruning (default: None)
  -v, --verbose         Print additional info (default: False)
~~~



