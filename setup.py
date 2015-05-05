#!/usr/bin/env python

import os
from setuptools import setup
import imp
import glob
import traceback

__version__ = imp.load_source('l2d.version', 'l2d/version.py').__version__

scripts = []
for f in glob.glob('l2d/scripts/*.py'):
    try:
        name = os.path.splitext(os.path.basename(f))[0]
        if name not in ['__init__']:
            scripts.append('l2d_%s = l2d.scripts.%s:main' % (name, name.lower()))
    except:
        print traceback.format_exc()

setup(
    name='lidar2dems',
    version=__version__,
    description='Utilities for creating DEMs from lidar data',
    author='Matthew Hanson',
    author_email='matt.a.hanson@gmail.com',
    packages=['l2d'],
    #requirements=['gippy', 'lxml'],
    entry_points={'console_scripts': scripts}
)
