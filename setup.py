#!/usr/bin/env python

from distutils.core import setup

setup(name='python-graphenelib',
      version='0.1',
      description='Python libraries for Graphene',
      long_description=open('README.md').read(),
      author='Fabian Schuh',
      author_email='<Fabian@Graphene.org>',
      maintainer='Fabian Schuh',
      maintainer_email='<Fabian@Graphene.org>',
      url='http://www.github.com/xeroc/python-graphenelib',
      packages=['graphenelib'],
      package_data={
          'graphenelib'  :  [ 'paperwallet/BitAssets/*', 
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
