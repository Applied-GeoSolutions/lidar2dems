#!/usr/bin/env python

from mayavi import mlab
import gippy

img = gippy.GeoImage('DTM_r3.00.idw.tif')
arr = img[0].Read()

mlab.figure(size=(640, 800), bgcolor=(0.16, 0.28, 0.46))

mlab.surf(arr, warp_scale=0.2)

mlab.show()
