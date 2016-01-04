import ecdsa
import hashlib
from binascii import hexlify, unhexlify
import unittest
import sys
import re
import os

from graphenebase.base58 import ripemd160, Base58
import graphenebase.dictionary as BrainKeyDictionary

""" This class and the methods require python3 """
assert sys.version_info[0] == 3, "graphenelib requires python3"


class BrainKey(object) :
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

    def __init__(self, brainkey=None, sequence=0):
        if brainkey is None :
            self.brainkey = self.suggest()
        else :
            self.brainkey = self.normalize(brainkey).strip()
        self.sequence = sequence

    def next_sequence(self) :
        """ Increment the sequence number by 1 """
        self.sequence += 1
        return self

    def normalize(self, brainkey) :
        """ Correct formating with single whitespace syntax and no trailing space """
        return " ".join(re.compile("[\t\n\v\f\r ]+").split(brainkey))

    def get_brainkey(self) :
        """ Return brain key of this instance """
        return self.normalize(self.brainkey)

    def get_private(self) :
        """ Derive private key from the brain key and the current sequence
            number
        """
        encoded = "%s %d" % (self.brainkey, self.sequence)
        a = bytes(encoded, 'ascii')
        s = hashlib.sha256(hashlib.sha512(a).digest()).digest()
        return PrivateKey(hexlify(s).decode('ascii'))

    def suggest(self):
        """ Suggest a new random brain key. Randomness is provided by the
            operating system using ``os.urandom()``.
        """
        word_count = 16
        brainkey = [None] * word_count
        dict_lines = BrainKeyDictionary.words.split(',')
        assert len(dict_lines) == 49744
        for j in range(0, word_count) :
            num = int.from_bytes(os.urandom(2), byteorder="little")
            rndMult = num / 2 ** 16  # returns float between 0..1 (inclusive)
            wIdx = round(len(dict_lines) * rndMult)
            brainkey[j] = dict_lines[wIdx]
        return " ".join(brainkey).upper()


class Address(object):
    """ Address class

        This class serves as an address representation for Public Keys.

        :param str address: Base58 encoded address (defaults to ``None``)
        :param str pubkey: Base58 encoded pubkey (defaults to ``None``)
        :param str prefix: Network prefix (defaults to ``BTS``)

        Example::

           Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi")

    """
    def __init__(self, address=None, pubkey=None, prefix="BTS"):
        if pubkey is not None :
            self._pubkey  = Base58(pubkey, prefix=prefix)
            self._address = None
        elif address is not None :
            self._pubkey  = None
            self._address = Base58(address, prefix=prefix)
        else :
            raise Exception("Address has to be initialized by either the " +
                            "pubkey or the address.")

    def derivesha256address(self):
        """ Derive address using ``RIPEMD160(SHA256(x))`` """
        pkbin         = unhexlify(repr(self._pubkey))
        addressbin    = ripemd160(hexlify(hashlib.sha256(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))

    def derivesha512address(self):
        """ Derive address using ``RIPEMD160(SHA512(x))`` """
        pkbin         = unhexlify(repr(self._pubkey))
        addressbin    = ripemd160(hexlify(hashlib.sha512(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))

    def __repr__(self) :
        """ Gives the hex representation of the ``GrapheneBase58CheckEncoded``
            Graphene address.
        """
        return repr(self.derivesha512address())

    def __str__(self) :
        """ Returns the readable Graphene address. This call is equivalent to
            ``format(Address, "BTS")``
        """
        return format(self, "BTS")

    def __format__(self, _format) :
        """  May be issued to get valid "MUSE", "PLAY" or any other Graphene compatible
            address with corresponding prefix.
        """
        if self._address is None :
            if _format.lower() == "btc" :
                return format(self.derivesha256address(), _format)
            else :
                return format(self.derivesha512address(), _format)
        else :
            return format(self._address, _format)

    def __bytes__(self) :
        """ Returns the raw content of the ``Base58CheckEncoded`` address """
        if self._address is None :
            return bytes(self.derivesha512address())
        else :
            return bytes(self._address)


class PublicKey(Address):
    """ This class deals with Public Keys and inherits ``Address``.

        :param str pk: Base58 encoded public key

        Example:::

           PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL")

        .. note:: By default, graphene-based networks deal with **compressed**
                  public keys. If an **uncompressed** key is required, the
                  method ``unCompressed`` can be used::

                      PublicKey("xxxxx").unCompressed()

    """
    def __init__(self, pk, prefix=None):
        self._pk     = Base58(pk, prefix=prefix)
        self.address = Address(pubkey=pk, prefix=prefix)
        self.pubkey = self._pk

    def _derive_y_from_x(self, x, is_even):
        """ Derive y point from x point """
        curve = ecdsa.SECP256k1.curve
        # The curve equation over F_p is:
        #   y^2 = x^3 + ax + b
        a, b, p = curve.a(), curve.b(), curve.p()
        alpha = (pow(x, 3, p) + a * x + b) % p
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, p)
        if (beta % 2) != is_even :
            beta = p - beta
        return beta

    def unCompressed(self):
        """ Derive uncompressed key """
        public_key = repr(self._pk)
        prefix = public_key[0:2]
        if prefix == "04":
            return public_key
        assert prefix == "02" or prefix == "03"
        x = int(public_key[2:], 16)
        y = self._derive_y_from_x(x, (prefix == "02"))
        key = '04' + '%064x' % x + '%064x' % y
        return key

    def point(self) :
        """ Return the point for the public key """
        string = unhexlify(self.unCompressed())
        return ecdsa.VerifyingKey.from_string(string[1:], curve=ecdsa.SECP256k1).pubkey.point

    def __repr__(self) :
        """ Gives the hex representation of the Graphene public key. """
        return repr(self._pk)

    def __str__(self) :
        """ Returns the readable Graphene public key. This call is equivalent to
            ``format(PublicKey, "BTS")``
        """
        return format(self._pk, "BTS")

    def __format__(self, _format) :
        """ Formats the instance of :doc:`Base58 <base58>` according to ``_format`` """
        return format(self._pk, _format)

    def __bytes__(self) :
        """ Returns the raw public key """
        return bytes(self._pk)


class PrivateKey(PublicKey):
    """ Derives the compressed and uncompressed public keys and
        constructs two instances of ``PublicKey``:

        :param str wif: Base58check-encoded wif key

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
    def __init__(self,wif=None):
        if wif == None :
            import os
            self._wif = Base58(hexlify(os.urandom(32)).decode('ascii'))
        elif isinstance(wif, Base58) :
            self._wif = wif
        else :
            self._wif = Base58(wif)
        # compress pubkeys only
        self._pubkeyhex, self._pubkeyuncompressedhex = self.compressedpubkey()
        self.pubkey               = PublicKey(self._pubkeyhex)
        self.uncompressed         = PublicKey(self._pubkeyuncompressedhex)
        self.uncompressed.address = Address(pubkey=self._pubkeyuncompressedhex)
        self.address              = Address(pubkey=self._pubkeyhex)

    def compressedpubkey(self):
        """ Derive uncompressed public key """
        secret = unhexlify(repr(self._wif))
        order  = ecdsa.SigningKey.from_string(secret, curve=ecdsa.SECP256k1).curve.generator.order()
        p      = ecdsa.SigningKey.from_string(secret, curve=ecdsa.SECP256k1).verifying_key.pubkey.point
        x_str  = ecdsa.util.number_to_string(p.x(), order)
        y_str  = ecdsa.util.number_to_string(p.y(), order)
        compressed   = hexlify(bytes(chr(2 + (p.y() & 1)),'ascii') + x_str        ).decode('ascii')
        uncompressed = hexlify(bytes(chr(4)              ,'ascii') + x_str + y_str).decode('ascii')
        return([compressed, uncompressed])

    def __format__(self,_format) :
        """ Formats the instance of :doc:`Base58 <base58>` according to
            ``_format``
        """
        return format(self._wif,_format)

    def __repr__(self) :
        """ Gives the hex representation of the Graphene private key."""
        return repr(self._wif)

    def __str__(self) :
        """ Returns the readable (uncompressed wif format) Graphene private key. This
            call is equivalent to ``format(PrivateKey, "WIF")``
        """
        return format(self._wif,"WIF")

    def __bytes__(self) :
        """ Returns the raw private key """
        return bytes(self._wif)

class Testcases(unittest.TestCase) :
    def test_B85hexgetb58_btc(self):
        self.assertEqual([   "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",
                             "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S",
                             "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                             "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                             "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                             "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49",
                             "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131",
                             "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e",
                             "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e",
                           ],[
                             format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"),"WIF"),
                             format(Base58("5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"),"WIF"),
                             format(Base58("0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"),"WIF"),
                             format(Base58("6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"),"WIF"),
                             format(Base58("b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"),"WIF"),
                             repr(Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")),
                             repr(Base58("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")),
                             repr(Base58("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                             repr(Base58("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                             ])
    def test_B85hexgetb58(self):
        self.assertEqual([   'BTS2CAbTi1ZcgMJ5otBFZSGZJKJenwGa9NvkLxsrS49Kr8JsiSGc',
                             'BTShL45FEyUVSVV1LXABQnh4joS9FsUaffRtsdarB5uZjPsrwMZF',
                             'BTS7DQR5GsfVaw4wJXzA3TogDhuQ8tUR2Ggj8pwyNCJXheHehL4Q',
                             'BTSqc4QMAJHAkna65i8U4b7nkbWk4VYSWpZebW7JBbD7MN8FB5sc',
                             'BTS2QAVTJnJQvLUY4RDrtxzX9jS39gEq8gbqYMWjgMxvsvZTJxDSu'
                           ],[
                             format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"),"BTS"),
                             format(Base58("5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"),"BTS"),
                             format(Base58("0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"),"BTS"),
                             format(Base58("6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"),"BTS"),
                             format(Base58("b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"),"BTS")])
    def test_Adress(self):
        self.assertEqual([
                            format(Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi"),"BTS"),
                            format(Address("BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112" ),"BTS"),
                            format(Address("BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk"),"BTS"),
                            format(Address("BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL"),"BTS"),
                            format(Address("BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr"),"BTS"),
                        ],[
                            "BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi",
                            "BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112",
                            "BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk",
                            "BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL",
                            "BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr",
                            ])
    def test_PubKey(self):
        self.assertEqual([
                            format(PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL", prefix="BTS").address,"BTS"),
                            format(PublicKey("BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT", prefix="BTS").address,"BTS"),
                            format(PublicKey("BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw", prefix="BTS").address,"BTS"),
                            format(PublicKey("BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V", prefix="BTS").address,"BTS"),
                            format(PublicKey("BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra", prefix="BTS").address,"BTS")
                         ],[
                             "BTS66FCjYKzMwLbE3a59YpmFqA9bwporT4L3",
                             "BTSKNpRuPX8KhTBsJoFp1JXd7eQEsnCpRw3k",
                             "BTS838ENJargbUrxXWuE2xD9HKjQaS17GdCd",
                             "BTSNsrLFWTziSZASnNJjWafFtGBfSu8VG8KU",
                             "BTSDjAGuXzk3WXabBEgKKc8NsuQM412boBdR"
                         ])
    def test_btsprivkey(self):
        self.assertEqual([
                            format(PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd").address,"BTS"),
                            format(PrivateKey("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S").address,"BTS"),
                            format(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq").address,"BTS"),
                            format(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R").address,"BTS"),
                            format(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7").address,"BTS")
                        ],[
                            "BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi",
                            "BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112",
                            "BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk",
                            "BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL",
                            "BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr",
                        ])
    def test_btcprivkey(self):
        self.assertEqual([
                            format(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq").uncompressed.address,"BTC"),
                            format(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R").uncompressed.address,"BTC"),
                            format(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7").uncompressed.address,"BTC"),
                        ],[
                            "1G7qw8FiVfHEFrSt3tDi6YgfAdrDrEM44Z",
                            "12c7KAAZfpREaQZuvjC5EhpoN6si9vekqK",
                            "1Gu5191CVHmaoU3Zz3prept87jjnpFDrXL",
                        ])

    def test_PublicKey(self):
        self.assertEqual([
                            str(PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",prefix="BTS")),
                            str(PublicKey("BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",prefix="BTS")),
                            str(PublicKey("BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",prefix="BTS")),
                            str(PublicKey("BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",prefix="BTS")),
                            str(PublicKey("BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",prefix="BTS"))
                         ],[
                            "BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                            "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                            "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                            "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                            "BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra"
                         ])

    def test_Privatekey(self):
        self.assertEqual([
                            str(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                            str(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                            str(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
                            repr(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                            repr(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                            repr(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
                        ],[
                            "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                            "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                            "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                            '0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e',
                            '6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e',
                            'b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8'
                        ])

    def test_BrainKey(self):
        self.assertEqual([
                           str(BrainKey("COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO").get_private()),
                           str(BrainKey("NAK TILTING MOOTING TAVERT SCREENY MAGIC BARDIE UPBORNE CONOID MAUVE CARBON NOTAEUM BITUMEN HOOEY KURUMA COWFISH").get_private()),
                           str(BrainKey("CORKITE CORDAGE FONDISH UNDER FORGET BEFLEA OUTBUD ZOOGAMY BERLINE ACANTHA STYLO YINCE TROPISM TUNKET FALCULA TOMENT").get_private()),
                           str(BrainKey("MURZA PREDRAW FIT LARIGOT CRYOGEN SEVENTH LISP UNTAWED AMBER CRETIN KOVIL TEATED OUTGRIN POTTAGY KLAFTER DABB").get_private()),
                           str(BrainKey("VERDICT REPOUR SUNRAY WAMBLY UNFILM UNCOUS COWMAN REBUOY MIURUS KEACORN BENZOLE BEMAUL SAXTIE DOLENT CHABUK BOUGHED").get_private()),
                           str(BrainKey("HOUGH TRUMPH SUCKEN EXODY MAMMATE PIGGIN CRIME TEPEE URETHAN TOLUATE BLINDLY CACOEPY SPINOSE COMMIE GRIECE FUNDAL").get_private()),
                           str(BrainKey("OERSTED ETHERIN TESTIS PEGGLE ONCOST POMME SUBAH FLOODER OLIGIST ACCUSE UNPLAT OATLIKE DEWTRY CYCLIZE PIMLICO CHICOT").get_private()),
                        ],[
                            "5JfwDztjHYDDdKnCpjY6cwUQfM4hbtYmSJLjGd9KTpk9J4H2jDZ",
                            "5JcdQEQjBS92rKqwzQnpBndqieKAMQSiXLhU7SFZoCja5c1JyKM",
                            "5JsmdqfNXegnM1eA8HyL6uimHp6pS9ba4kwoiWjjvqFC1fY5AeV",
                            "5J2KeFptc73WTZPoT1Sd59prFep6SobGobCYm7T5ZnBKtuW9RL9",
                            "5HryThsy6ySbkaiGK12r8kQ21vNdH81T5iifFEZNTe59wfPFvU9",
                            "5Ji4N7LSSv3MAVkM3Gw2kq8GT5uxZYNaZ3d3y2C4Ex1m7vshjBN",
                            "5HqSHfckRKmZLqqWW7p2iU18BYvyjxQs2sksRWhXMWXsNEtxPZU",
                        ])

def keyinfo(private_key) :
    print("-"*80)
    print("Private Key             : " + format(private_key,"WIF"))
    print("Secret Exponent (hex)   : " + repr(private_key))
    print("-"*80)
    print("BTC uncomp. Pubkey (hex): " + repr(private_key.uncompressed.pubkey))
    print("BTC Address (uncompr)   : " + format(private_key.uncompressed.address,"BTC"))
    print("-"*80)
    print("BTC comp. Pubkey (hex)  : " + repr(private_key.pubkey))
    print("BTC Address (compr)     : " + format(private_key.address,"BTC"))
    print("-"*80)                      
    print("BTS PubKey (hex)        : " + repr(private_key.pubkey))
    print("BTS PubKey              : " + format(private_key.pubkey,"BTS"))
    print("BTS Address             : " + format(private_key.address,"BTS"))
    print("-"*80)

if __name__ == '__main__':
    unittest.main()

    # Generate a random private key or take it from input as WIF
    #import sys
    #if len( sys.argv ) < 2 : keyinfo(PrivateKey())
    #else                   : keyinfo(PrivateKey(sys.argv[1]))
