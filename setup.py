#!/usr/bin/env python

from setuptools import setup
import imp

__version__ = imp.load_source('lidar2dems.version', 'lidar2dems/version.py').__version__

setup(
    name='lidar2dems',
    version=__version__,
    description='Utilities for creating DEMs from lidar data',
    author='Matthew Hanson',
    author_email='matt.a.hanson@gmail.com',
    packages=['lidar2dems'],
#    entry_points={'console_scripts': console_scripts}
)
