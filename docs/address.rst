Address Module
==============

Requirements
------------
* python-ecdsa

Usage
-----

.. note:: Everthing returned by any method of this module is an instance of the
          :doc:`base58`

This module contains the following classes:

``Address``
^^^^^^^^^^^
Derives addresses of ``PublicKeys`` and represents it according to
``Base58CheckEncode`` or ``GrapheneBase58CheckEncode``.

* ``bytes(Address)``
    Returns the raw content of the ``GrapheneBase58CheckEncoded`` address
* ``str(Address)``
    Returns the readable Graphene address. This call is equivalent to ``format(Address, "BTS")``
* ``repr(Address)``
    Gives the hex representation of the ``GrapheneBase58CheckEncoded`` Graphene address.
* ``format(Address,"btc")``
    Uses the raw address/public key to derive a valid Bitcoin address.
* ``format(Address,"*")``
    May be issued to get valid "MUSIC", "PLAY" or any other Graphene compatible
    address with corresponding prefix.

Example:::

   Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi")

``PublicKey``
^^^^^^^^^^^^^
Inherits ``Address``.

* ``bytes(PublicKey)``
    Returns the raw public key
* ``str(PublicKey)``
    Returns the readable Graphene public key. This call is equivalent to ``format(PublicKey, "BTS")``
*  ``repr(PublicKey)``
    Gives the hex representation of the Graphene public key.
*  ``format(PublicKey,_format)``
    Formats the instance of :doc:`Base58 <base58>` according to ``_format``

Example:::

   PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL")
  
``PrivateKey``
^^^^^^^^^^^^^^
Inherits ``PublicKey``. Derives the compressed and uncompressed public keys and
constructs two instances of ``PublicKey``

* ``bytes(PrivateKey)``
    Returns the raw private key
* ``str(PrivateKey)``
    Returns the readable (uncompressed wif format) Graphene private key. This
    call is equivalent to ``format(PrivateKey, "WIF")``
* ``repr(PrivateKey)``
    Gives the hex representation of the Graphene private key.
* ``format(PrivateKey,_format)``
    Formats the instance of :doc:`Base58 <base58>` according to ``_format``

Example:::

   PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")

Format vs. Repr
^^^^^^^^^^^^^^^

.. code-block:: python

    print("Private Key             : " + format(private_key,"WIF"))
    print("Secret Exponent (hex)   : " + repr(private_key))
    print("BTS PubKey (hex)        : " + repr(private_key.pubkey))
    print("BTS PubKey              : " + format(private_key.pubkey, "BTS"))
    print("BTS Address             : " + format(private_key.address,"BTS"))

Output::

    Private Key             : 5Jdv8JHh4r2tUPtmLq8hp8DkW5vCp9y4UGgj6udjJQjG747FCMc
    Secret Exponent (hex)   : 6c2662a6ac41bd9132a9f846847761ab4f80c82d519cdf92f40dfcd5e97ec5b5
    BTS PubKey (hex)        : 021760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de
    BTS PubKey              : BTS54nWRnewkASXXTwpn3q4q8noadzXmw4y1KpED3grup7VrDDRmx
    BTS Address             : BTSCmUwH8G1t3VSZRH5kwxx31tiYDNrzWvyW

Compressed vs. Uncompressed
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    print("BTC uncomp. Pubkey (hex): " + repr(private_key.uncompressed.pubkey))
    print("BTC Address (uncompr)   : " + format(private_key.uncompressed.address,"BTC"))
    print("BTC comp. Pubkey (hex)  : " + repr(private_key.pubkey))
    print("BTC Address (compr)     : " + format(private_key.address,"BTC"))

Output::

    BTC uncomp. Pubkey (hex): 041760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de4d5abd46cabab34222023cd9034e1e6c0377fac5579a9c01e46b9498529aaf46
    BTC Address (uncompr)   : 1JidAV2npbyLn77jGYQtkpJDjx6Yt5eJSh
    BTC comp. Pubkey (hex)  : 021760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de
    BTC Address (compr)     : 1GZ1JCW3kdL4LoCWbzHK4oV6V8JcUGG8HF
