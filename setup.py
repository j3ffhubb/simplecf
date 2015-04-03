#!/usr/bin/env python
"""
This file is part of the simplecf project, Copyright simplecf Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

import setuptools
from glob import glob
import os
import sys

simplecf_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "bin")

sys.path.insert(0, simplecf_dir)

import simplecf

setuptools.setup(
    name="simplecf",
    version=simplecf.__version__,
    author="Jeff Hubbard",
    author_email='j3ffhubb@redhat.com',
    license='GPL 3.0',
    description='Templating system for AWS Cloudformation',
    url='https://github.com/j3ffhubb/simplecf',
    #packages=setuptools.find_packages(),
    #include_package_data=True,
    install_requires=['argparse', 'boto', 'pystache'],
    scripts=('bin/simplecf.py',),
)
