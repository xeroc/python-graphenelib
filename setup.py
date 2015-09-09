#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
      name='graphene',
      version='0.1',
      description='Python libraries for Graphene',
      long_description=open('README.md').read(),

      author='Fabian Schuh',
      author_email='<Fabian@BitShares.eu>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@BitShares.eu>',
      url='http://www.github.com/xeroc/python-graphene',

      packages=["grapheneapi",
                "graphenebase",
                #"grapheneextra",
                #"graphenemarket"
                ],
      package_data={
          'extra'  :  [ 'paperwallet/BitAssets/*', 
                        'paperwallet/designs/*',
                      ],
          },
      classifiers=['License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Topic :: Office/Business :: Financial',
                   ]
    )
