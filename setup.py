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
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.3.11'

setup(name='graphenelib',
      version=VERSION,
      description='Python library for graphene-based blockchains',
      long_description=open('README.md').read(),
      download_url='https://github.com/xeroc/python-graphenelib/tarball/' + VERSION,
      author='Fabian Schuh',
      author_email='<Fabian@BitShares.eu>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@BitShares.eu>',
      url='http://www.github.com/xeroc/python-graphenelib',
      keywords=['bitshares', 'muse', 'library', 'api',
                'rpc', 'coin', 'tradingbot', 'exchange'],
      packages=["grapheneapi",
                "graphenebase",
                "grapheneextra",
                "grapheneexchange",
                ],
      install_requires=["autobahn>=0.12.1",
                        "requests>=2.9.1",
                        "pycrypto>=2.6.1",
                        "scrypt>=0.7.1",
                        "ecdsa>=0.13",
                        "websocket-client>=0.37.0",
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
      include_package_data=True,
      )
