#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='stickytape',
    version='0.1.13',
    description='Convert Python packages into a single script',
    long_description=read("README.rst"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/stickytape',
    packages=['stickytape'],
    entry_points={
        "console_scripts": [
            "stickytape=stickytape.main:main"
        ]
    },
)
