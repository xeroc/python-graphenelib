import ecdsa
import hashlib
from binascii import hexlify,unhexlify
from graphenelib.base58 import ripemd160,Base58
import unittest
import sys

"""
This class and the methods require python3
"""
assert sys.version_info[0] == 3, "graphenelib requires python3"

class Address(object):
    def __init__(self,address=None,pubkey=None):
        if pubkey is not None :
            self._pubkey  = Base58(pubkey)
            self._address = None
        elif address is not None :
            self._pubkey  = None
            self._address = Base58(address)
        else :
            raise Exception("Address has to be initialized by either the pubkey or the address.")

    def derivesha256address(self):
        pkbin         = unhexlify(repr(self._pubkey))
        addressbin    = ripemd160(hexlify(hashlib.sha256(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))

    def derivesha512address(self):
        pkbin         = unhexlify(repr(self._pubkey))
        addressbin    = ripemd160(hexlify(hashlib.sha512(pkbin).digest()))
        return Base58(hexlify(addressbin).decode('ascii'))
    """
    Returns hex value of object
    """
    def __repr__(self) :
        return repr(self.derivesha512address())
    """
    Return BTS-base58CheckEncoded string of data
    """
    def __str__(self) :
        return format(self, "BTS")
    """
    Return formated address
    """
    def __format__(self,_format) :
        if self._address == None :
            if _format.lower() == "btc" : 
                return format(self.derivesha256address(),_format)
            else :
                return format(self.derivesha512address(),_format)
        else :
            return format(self._address,_format)
    """
    Return raw bytes
    """
    def __bytes__(self) :
        if self._address == None :
            return bytes(self.derivesha512address())
        else :
            return bytes(self._address)

class PublicKey(Address):
    def __init__(self,pk,prefix=None):
        self._pk     = Base58(pk,prefix=prefix)
        self.address = Address(pubkey=pk)
        self.pubkey = self._pk
    """
    Returns hex value of object
    """
    def __repr__(self) :
        return repr(self._pk)
    """
    Return BTS-base58CheckEncoded string of data
    """
    def __str__(self) :
        return format(self._pk,"BTS")
    """
    Return formated pubkey
    """
    def __format__(self,_format) :
        return format(self._pk, _format)
    """
    Return raw bytes
    """
    def __bytes__(self) :
        return bytes(self._pk)

class PrivateKey(PublicKey):
    def __init__(self,wif=None):
        if wif == None :
            import os
            self._wif = Base58(hexlify(os.urandom(32)).decode('ascii'))
        else :
            self._wif = Base58(wif)
        # compress pubkeys only
        self._pubkeyhex, self._pubkeyuncompressedhex = self.compressedpubkey()
        self.pubkey               = PublicKey(self._pubkeyhex)
        self.uncompressed         = PublicKey(self._pubkeyuncompressedhex)
        self.uncompressed.address = Address(pubkey=self._pubkeyuncompressedhex)
        self.address              = Address(pubkey=self._pubkeyhex)

    def compressedpubkey(self):
        secret = unhexlify(repr(self._wif))
        order  = ecdsa.SigningKey.from_string(secret, curve=ecdsa.SECP256k1).curve.generator.order()
        p      = ecdsa.SigningKey.from_string(secret, curve=ecdsa.SECP256k1).verifying_key.pubkey.point
        x_str  = ecdsa.util.number_to_string(p.x(), order)
        y_str  = ecdsa.util.number_to_string(p.y(), order)
        compressed   = hexlify(bytes(chr(2 + (p.y() & 1)),'ascii') + x_str        ).decode('ascii')
        uncompressed = hexlify(bytes(chr(4)              ,'ascii') + x_str + y_str).decode('ascii')
        return([compressed, uncompressed])

    """
    Return formated pubkey
    """
    def __format__(self,_format) :
        return format(self._wif,_format)
    """
    Returns hex value of object
    """
    def __repr__(self) :
        return repr(self._wif)
    """
    Return BTS-base58CheckEncoded string of data
    """
    def __str__(self) :
        return format(self._wif,"WIF")
    """
    Return raw bytes
    """
    def __bytes__(self) :
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
