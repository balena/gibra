#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imp
import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

if sys.version_info[0] < 3:
    raise "Must be using Python 3"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

gibra = imp.load_source('gibra', './gibra')

setup(
    name='gibra',
    version=gibra.__version__,
    description='Git Binary Repository Assistant',
    long_description=long_description,
    url='https://github.com/balena/gibra',
    author='Guilherme Balena Versiani',
    author_email='guibv@yahoo.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Version Control :: Git',
        'Framework :: Flask',
    ],
    keywords='git binary repository manager assistant',
    packages=find_packages(),
    platforms=["all"],
    install_requires=gibra.__requirements__,
    scripts=['gibra'],
)
