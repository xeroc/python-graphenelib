#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

VERSION = '0.3.6'

setup(name='graphenelib',
      version=VERSION,
      description='Python library for graphene-based blockchains',
      long_description=open('README.rst').read(),
      download_url='https://github.com/xeroc/python-graphenelib/tarball/' + VERSION,
      author='Fabian Schuh',
      author_email='<Fabian@BitShares.eu>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@BitShares.eu>',
      url='http://www.github.com/xeroc/python-graphene',
      keywords=['bitshares', 'muse', 'library', 'api',
                'rpc', 'coin', 'tradingbot', 'exchange'],
      packages=["grapheneapi",
                "graphenebase",
                "grapheneextra",
                "grapheneexchange",
                ],
      classifiers=['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Topic :: Office/Business :: Financial',
                   ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      )
