#!/usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A collection of useful python modules',
    'author': 'bluec0re',
    'url': 'https://github.com/bluec0re/python-helperlib.git',
    'download_url': 'https://github.com/bluec0re/python-helperlib/archive/master.zip',
    'author_email': 'coding@bluec0re.eu',
    'version': '0.5.1',
    'install_requires': ['six'],
    'packages': ['helperlib'],
    'scripts': [
        'bin/hl-hexdump.py',
        'bin/hl-unhexdump.py',
        'bin/hl-hexII.py',
        'bin/hl-unhexII.py',
    ],
    'name': 'helperlib',
}

setup(**config)
