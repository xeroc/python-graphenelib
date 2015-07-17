Base58 Class
============

Requirements
------------
* python-ecdsa

Usage
-----

This module provides following class:

Base58(object)
^^^^^^^^^^^^^^

* ``bytes(Base58)``
    Returns the raw data
* ``str(Base58)``
    Returns the readable ``GrapheneBase58CheckEncoded`` data.
*  ``repr(Base58)``
    Gives the hex representation of the data.
*  ``format(Base58,_format)``
    Formats the instance according to ``_format``:

    * ``btc``::

            return base58CheckEncode(0x80, self._hex)

    * ``wif``::

            return base58CheckEncode(0x00, self._hex)

    * ``bts``::

            return _format + str(self)

Examples:::

        format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"),"wif")
        repr(Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"))

Output:::

       "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"
       "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"
