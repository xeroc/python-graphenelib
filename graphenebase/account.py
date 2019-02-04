# -*- coding: utf-8 -*-
from __future__ import absolute_import

import hashlib
import re
import os

from binascii import hexlify, unhexlify
from .base58 import ripemd160, Base58, doublesha256
from .dictionary import words as BrainKeyDictionary
from .utils import _bytes
from .prefix import Prefix

import ecdsa


class PasswordKey(Prefix):
    """ This class derives a private key given the account name, the
        role and a password. It leverages the technology of Brainkeys
        and allows people to have a secure private key by providing a
        passphrase only.
    """

    def __init__(self, account, password, role="active", prefix=None):
        self.set_prefix(prefix)
        self.account = account
        self.role = role
        self.password = password

    def get_private(self):
        """ Derive private key from the brain key and the current sequence
            number
        """
        a = _bytes(self.account + self.role + self.password)
        s = hashlib.sha256(a).digest()
        return PrivateKey(hexlify(s).decode("ascii"), prefix=self.prefix)

    def get_public(self):
        return self.get_private().pubkey

    def get_private_key(self):
        return self.get_private()

    def get_public_key(self):
        return self.get_public()


class BrainKey(Prefix):
    """Brainkey implementation similar to the graphene-ui web-wallet.

        :param str brainkey: Brain Key
        :param int sequence: Sequence number for consecutive keys

        Keys in Graphene are derived from a seed brain key which is a string of
        16 words out of a predefined dictionary with 49744 words. It is a
        simple single-chain key derivation scheme that is not compatible with
        BIP44 but easy to use.

        Given the brain key, a private key is derived as::

            privkey = SHA256(SHA512(brainkey + " " + sequence))

        Incrementing the sequence number yields a new key that can be
        regenerated given the brain key.

    """

    def __init__(self, brainkey=None, sequence=0, prefix=None):
        self.set_prefix(prefix)
        if not brainkey:
            self.brainkey = BrainKey.suggest()
        else:
            self.brainkey = self.normalize(brainkey).strip()
        self.sequence = sequence

    def __next__(self):
        """ Get the next private key (sequence number increment) for
            iterators
        """
        return self.next_sequence()

    def next_sequence(self):
        """ Increment the sequence number by 1 """
        self.sequence += 1
        return self

    def normalize(self, brainkey):
        """ Correct formating with single whitespace syntax and no trailing
            space
        """
        return " ".join(re.compile("[\t\n\v\f\r ]+").split(brainkey))

    def get_brainkey(self):
        """ Return brain key of this instance """
        return self.normalize(self.brainkey)

    def get_private(self):
        """ Derive private key from the brain key and the current sequence
            number
        """
        encoded = "%s %d" % (self.brainkey, self.sequence)
        a = _bytes(encoded)
        s = hashlib.sha256(hashlib.sha512(a).digest()).digest()
        return PrivateKey(hexlify(s).decode("ascii"), prefix=self.prefix)

    def get_blind_private(self):
        """ Derive private key from the brain key (and no sequence number)
        """
        a = _bytes(self.brainkey)
        return PrivateKey(hashlib.sha256(a).hexdigest(), prefix=self.prefix)

    def get_public(self):
        return self.get_private().pubkey

    def get_private_key(self):
        return self.get_private()

    def get_public_key(self):
        return self.get_public()

    @staticmethod
    def suggest():
        """ Suggest a new random brain key. Randomness is provided by the
            operating system using ``os.urandom()``.
        """
        word_count = 16
        brainkey = [None] * word_count
        dict_lines = BrainKeyDictionary.split(",")
        assert len(dict_lines) == 49744
        for j in range(0, word_count):
            num = int.from_bytes(os.urandom(2), byteorder="little")
            rndMult = num / 2 ** 16  # returns float between 0..1 (inclusive)
            wIdx = round(len(dict_lines) * rndMult)
            brainkey[j] = dict_lines[wIdx]
        return " ".join(brainkey).upper()


class Address(Prefix):
    """ Address class

        This class serves as an address representation for Public Keys.

        :param str address: Base58 encoded address (defaults to ``None``)
        :param str pubkey: Base58 encoded pubkey (defaults to ``None``)
        :param str prefix: Network prefix (defaults to ``GPH``)

        Example::

           Address("GPHFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi")

    """

    def __init__(self, address, prefix=None):
        self.set_prefix(prefix)
        self._address = Base58(address, prefix=self.prefix)

    @classmethod
    def from_pubkey(cls, pubkey, compressed=True, version=56, prefix=None):
        """ Load an address provided the public key.

            Version: 56 => PTS
        """
        # Ensure this is a public key
        pubkey = PublicKey(pubkey, prefix=prefix or Prefix.prefix)
        if compressed:
            pubkey_plain = pubkey.compressed()
        else:
            pubkey_plain = pubkey.uncompressed()
        sha = hashlib.sha256(unhexlify(pubkey_plain)).hexdigest()
        rep = hexlify(ripemd160(sha)).decode("ascii")
        s = ("%.2x" % version) + rep
        result = s + hexlify(doublesha256(s)[:4]).decode("ascii")
        result = hexlify(ripemd160(result)).decode("ascii")
        return cls(result, prefix=pubkey.prefix)

    def __repr__(self):
        """ Gives the hex representation of the ``GrapheneBase58CheckEncoded``
            Graphene address.
        """
        return repr(self._address)

    def __str__(self):
        """ Returns the readable Graphene address. This call is equivalent to
            ``format(Address, "GPH")``
        """
        return format(self._address, self.prefix)

    def __format__(self, _format):
        """  May be issued to get valid "MUSE", "PLAY" or any other Graphene compatible
            address with corresponding prefix.
        """
        return format(self._address, _format)

    def __bytes__(self):
        """ Returns the raw content of the ``Base58CheckEncoded`` address """
        return bytes(self._address)


class GrapheneAddress(Address):
    """ Graphene Addresses are different. Hence we have a different class
    """

    @classmethod
    def from_pubkey(cls, pubkey, compressed=True, version=56, prefix=None):
        # Ensure this is a public key
        pubkey = PublicKey(pubkey, prefix=prefix or Prefix.prefix)
        if compressed:
            pubkey_plain = pubkey.compressed()
        else:
            pubkey_plain = pubkey.uncompressed()

        """ Derive address using ``RIPEMD160(SHA512(x))`` """
        addressbin = ripemd160(hashlib.sha512(unhexlify(pubkey_plain)).hexdigest())
        result = Base58(hexlify(addressbin).decode("ascii"))
        return cls(result, prefix=pubkey.prefix)


class PublicKey(Prefix):
    """ This class deals with Public Keys and inherits ``Address``.

        :param str pk: Base58 encoded public key
        :param str prefix: Network prefix (defaults to ``GPH``)

        Example:::

           PublicKey("GPH6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL")

        .. note:: By default, graphene-based networks deal with **compressed**
                  public keys. If an **uncompressed** key is required, the
                  method ``unCompressed`` can be used::

                      PublicKey("xxxxx").unCompressed()

    """

    def __init__(self, pk, prefix=None):
        self.set_prefix(prefix)
        if isinstance(pk, PublicKey):
            pk = format(pk, self.prefix)

        if str(pk).startswith("04"):
            # We only ever deal with compressed keys, so let's make it
            # compressed
            order = ecdsa.SECP256k1.order
            p = ecdsa.VerifyingKey.from_string(
                unhexlify(pk[2:]), curve=ecdsa.SECP256k1
            ).pubkey.point
            x_str = ecdsa.util.number_to_string(p.x(), order)
            pk = hexlify(chr(2 + (p.y() & 1)).encode("ascii") + x_str).decode("ascii")

        self._pk = Base58(pk, prefix=self.prefix)

    @property
    def pubkey(self):
        return self._pk

    @property
    def compressed_key(self):
        return PublicKey(self.compressed())

    def _derive_y_from_x(self, x, is_even):
        """ Derive y point from x point """
        curve = ecdsa.SECP256k1.curve
        # The curve equation over F_p is:
        #   y^2 = x^3 + ax + b
        a, b, p = curve.a(), curve.b(), curve.p()
        alpha = (pow(x, 3, p) + a * x + b) % p
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, p)
        if (beta % 2) == is_even:
            beta = p - beta
        return beta

    def compressed(self):
        """ returns the compressed key """
        return repr(self._pk)

    def uncompressed(self):
        """ Derive uncompressed key """
        public_key = repr(self._pk)
        prefix = public_key[0:2]
        assert prefix == "02" or prefix == "03"
        x = int(public_key[2:], 16)
        y = self._derive_y_from_x(x, (prefix == "02"))
        key = "04" + "%064x" % x + "%064x" % y
        return key

    def point(self):
        """ Return the point for the public key """
        string = unhexlify(self.unCompressed())
        return ecdsa.VerifyingKey.from_string(
            string[1:], curve=ecdsa.SECP256k1
        ).pubkey.point

    def child(self, offset256):
        """ Derive new public key from this key and a sha256 "offset" """
        a = bytes(self) + offset256
        s = hashlib.sha256(a).digest()
        return self.add(s)

    def add(self, digest256):
        """ Derive new public key from this key and a sha256 "digest" """
        from .ecdsa import tweakaddPubkey

        return tweakaddPubkey(self, digest256)

    @classmethod
    def from_privkey(cls, privkey, prefix=None):
        """ Derive uncompressed public key """
        privkey = PrivateKey(privkey, prefix=prefix or Prefix.prefix)
        secret = unhexlify(repr(privkey))
        order = ecdsa.SigningKey.from_string(
            secret, curve=ecdsa.SECP256k1
        ).curve.generator.order()
        p = ecdsa.SigningKey.from_string(
            secret, curve=ecdsa.SECP256k1
        ).verifying_key.pubkey.point
        x_str = ecdsa.util.number_to_string(p.x(), order)
        # y_str = ecdsa.util.number_to_string(p.y(), order)
        compressed = hexlify(chr(2 + (p.y() & 1)).encode("ascii") + x_str).decode(
            "ascii"
        )
        # uncompressed = hexlify(
        #    chr(4).encode('ascii') + x_str + y_str).decode('ascii')
        return cls(compressed, prefix=prefix or Prefix.prefix)

    def __repr__(self):
        """ Gives the hex representation of the Graphene public key. """
        return repr(self._pk)

    def __str__(self):
        """ Returns the readable Graphene public key. This call is equivalent to
            ``format(PublicKey, "GPH")``
        """
        return format(self._pk, self.prefix)

    def __format__(self, _format):
        """ Formats the instance of:doc:`Base58 <base58>` according to
            ``_format``
        """
        return format(self._pk, _format)

    def __bytes__(self):
        """ Returns the raw public key (has length 33)"""
        return bytes(self._pk)

    def __lt__(self, other):
        """ For sorting of public keys (due to graphene),
            we actually sort according to addresses
        """
        assert isinstance(other, PublicKey)
        return repr(self.address) < repr(other.address)

    def unCompressed(self):
        """ Alias for self.uncompressed() - LEGACY"""
        return self.uncompressed()

    @property
    def address(self):
        """ Obtain a GrapheneAddress from a public key
        """
        return GrapheneAddress.from_pubkey(repr(self), prefix=self.prefix)


class PrivateKey(Prefix):
    """ Derives the compressed and uncompressed public keys and
        constructs two instances of ``PublicKey``:

        :param str wif: Base58check-encoded wif key
        :param str prefix: Network prefix (defaults to ``GPH``)

        Example:::

            PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")

        Compressed vs. Uncompressed:

        * ``PrivateKey("w-i-f").pubkey``:
            Instance of ``PublicKey`` using compressed key.
        * ``PrivateKey("w-i-f").pubkey.address``:
            Instance of ``Address`` using compressed key.
        * ``PrivateKey("w-i-f").uncompressed``:
            Instance of ``PublicKey`` using uncompressed key.
        * ``PrivateKey("w-i-f").uncompressed.address``:
            Instance of ``Address`` using uncompressed key.

    """

    def __init__(self, wif=None, prefix=None):
        self.set_prefix(prefix)
        if wif is None:
            import os

            self._wif = Base58(hexlify(os.urandom(32)).decode("ascii"))
        elif isinstance(wif, PrivateKey):
            self._wif = wif._wif
        elif isinstance(wif, Base58):
            self._wif = wif
        else:
            self._wif = Base58(wif)

        # test for valid key by trying to obtain a public key
        assert len(repr(self._wif)) == 64

    @property
    def bitcoin(self):
        return BitcoinPublicKey.from_privkey(self)

    @property
    def address(self):
        return Address.from_pubkey(self.pubkey, prefix=self.prefix)

    @property
    def pubkey(self):
        return self.compressed

    @property
    def compressed(self):
        return PublicKey.from_privkey(self, prefix=self.prefix)

    @property
    def uncompressed(self):
        return PublicKey(self.pubkey.uncompressed(), prefix=self.prefix)

    def get_secret(self):
        """ Get sha256 digest of the wif key.
        """
        return hashlib.sha256(bytes(self)).digest()

    def derive_private_key(self, sequence):
        """ Derive new private key from this private key and an arbitrary
            sequence number
        """
        encoded = "%s %d" % (str(self), sequence)
        a = bytes(encoded, "ascii")
        s = hashlib.sha256(hashlib.sha512(a).digest()).digest()
        return PrivateKey(hexlify(s).decode("ascii"), prefix=self.pubkey.prefix)

    def child(self, offset256):
        """ Derive new private key from this key and a sha256 "offset"
        """
        a = bytes(self.pubkey) + offset256
        s = hashlib.sha256(a).digest()
        return self.derive_from_seed(s)

    def derive_from_seed(self, offset):
        """ Derive private key using "generate_from_seed" method.
            Here, the key itself serves as a `seed`, and `offset`
            is expected to be a sha256 digest.
        """
        seed = int(hexlify(bytes(self)).decode("ascii"), 16)
        z = int(hexlify(offset).decode("ascii"), 16)
        order = ecdsa.SECP256k1.order
        secexp = (seed + z) % order
        secret = "%0x" % secexp
        if len(secret) < 64: # left-pad with zeroes
            secret = ("0" * (64-len(secret))) + secret
        return PrivateKey(secret, prefix=self.pubkey.prefix)

    def __format__(self, _format):
        """ Formats the instance of:doc:`Base58 <base58>` according to
            ``_format``
        """
        return format(self._wif, _format)

    def __repr__(self):
        """ Gives the hex representation of the Graphene private key."""
        return repr(self._wif)

    def __str__(self):
        """ Returns the readable (uncompressed wif format) Graphene private key. This
            call is equivalent to ``format(PrivateKey, "WIF")``
        """
        return format(self._wif, "WIF")

    def __bytes__(self):  # pragma: no cover
        """ Returns the raw private key """
        return bytes(self._wif)


class BitcoinAddress(Address):
    @classmethod
    def from_pubkey(cls, pubkey, compressed=False, version=56, prefix=None):
        # Ensure this is a public key
        pubkey = PublicKey(pubkey)
        if compressed:
            pubkey = pubkey.compressed()
        else:
            pubkey = pubkey.uncompressed()

        """ Derive address using ``RIPEMD160(SHA256(x))`` """
        addressbin = ripemd160(hexlify(hashlib.sha256(unhexlify(pubkey)).digest()))
        return cls(hexlify(addressbin).decode("ascii"))

    def __str__(self):
        """ Returns the readable Graphene address. This call is equivalent to
            ``format(Address, "GPH")``
        """
        return format(self._address, "BTC")


class BitcoinPublicKey(PublicKey):
    @property
    def address(self):
        return BitcoinAddress.from_pubkey(repr(self))
