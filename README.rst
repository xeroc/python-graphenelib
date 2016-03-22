***************************
Python Library for Graphene
***************************

Python 3 library for Graphene 2.0!

+-----------+--------------------+------------------+
|           | Travis             | readthedocs      |
+-----------+--------------------+------------------+
| develop   | |Travis develop|   | |docs develop|   |
+-----------+--------------------+------------------+
| master    | |Travis master|    | |docs master|    |
+-----------+--------------------+------------------+

Installation
############

Install with `pip`:

::

    $ sudo apt-get install libffi-dev libssl-dev python-dev
    $ pip3 install graphenelib

Manual installation:

::

    $ git clone https://github.com/xeroc/python-graphenlib/
    $ cd python-graphenlib
    $ python3 setup.py install --user -r requirements.txt

Upgrade
#######

::

   $ pip install --user --upgrade -r requirements.txt graphenelib

Documentation
#############

Thanks to readthedocs.org, the documentation can be viewed at:

* http://python-graphenelib.readthedocs.org/en/latest/

Documentation is written with the help of `sphinx` and can be compile to
`html` with::

    cd docs
    make html

Licence
#######

See ``LICENCE.txt``

.. |Travis develop| image:: https://travis-ci.org/xeroc/python-graphenelib.png?branch=develop
   :target: https://travis-ci.org/xeroc/python-graphenelib
.. |Travis master| image:: https://travis-ci.org/xeroc/python-graphenelib.png?branch=master
   :target: https://travis-ci.org/xeroc/python-graphenelib
.. |Coverage develop| image:: https://coveralls.io/repos/xeroc/python-graphenelib/badge.png?branch=develop
   :target: https://coveralls.io/r/xeroc/python-graphenelib?branch=develop
.. |Coverage master| image:: https://coveralls.io/repos/xeroc/python-graphenelib/badge.png?branch=master
   :target: https://coveralls.io/r/xeroc/python-graphenelib?branch=master
.. |docs develop| image:: https://readthedocs.org/projects/python-graphenelib/badge/?version=develop
   :target: http://python-graphenelib.readthedocs.org/en/develop/
.. |docs master| image:: https://readthedocs.org/projects/python-graphenelib/badge/?version=latest
   :target: http://python-graphenelib.readthedocs.org/en/latest/
