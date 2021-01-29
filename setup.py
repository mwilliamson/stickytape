#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='stickytape',
    version='0.2.1',
    description='Convert Python packages into a single script',
    long_description=read("README.rst"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/stickytape',
    packages=['stickytape'],
    python_requires='>=3.4',
    license="BSD-2-Clause",
    entry_points={
        "console_scripts": [
            "stickytape=stickytape.main:main"
        ]
    },
)
