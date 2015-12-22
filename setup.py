#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
      name='graphenelib',
      version='v0.1.1',
      description='Python library for graphene-based blockchains',
      long_description=open('README.md').read(),
      download_url = 'https://github.com/xeroc/python-graphenelib/tarball/v0.1.1',
      author='Fabian Schuh',
      author_email='<Fabian@BitShares.eu>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@BitShares.eu>',
      url='http://www.github.com/xeroc/python-graphene',
      keywords = ['bitshares','muse','library','api','rpc','coin'],
      packages=["grapheneapi",
                "graphenebase",
                "grapheneextra",
                ],
      classifiers=['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Topic :: Office/Business :: Financial',
                   ]
    )
