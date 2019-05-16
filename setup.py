#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

VERSION = "1.1.18"
URL = "https://github.com/xeroc/python-graphenelib"

setup(
    name="graphenelib",
    version=VERSION,
    description="Python library for graphene-based blockchains",
    long_description=open("README.md").read(),
    download_url="{}/tarball/{}".format(URL, VERSION),
    author="Fabian Schuh",
    author_email="Fabian@chainsquad.com",
    maintainer="Fabian Schuh",
    maintainer_email="Fabian@chainsquad.com",
    url=URL,
    keywords=["graphene", "api", "rpc", "ecdsa", "secp256k1"],
    packages=["grapheneapi", "graphenebase", "graphenestorage", "graphenecommon"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ],
    install_requires=open("requirements.txt").readlines(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
)
