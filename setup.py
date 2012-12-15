#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='stickytape',
    version='0.1.7',
    description='Convert Python packages into a single script',
    long_description=read("README"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/stickytape',
    scripts=["scripts/stickytape"],
    packages=['stickytape'],
    install_requires=["argparse==1.2.1"],
)
