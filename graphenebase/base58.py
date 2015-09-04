from binascii import hexlify, unhexlify
import hashlib
import sys
import string
import unittest

"""
This class and the methods require python3
"""
assert sys.version_info[0] == 3, "graphenelib requires python3"

"""
Default Prefix
"""
PREFIX = "BTS"

"""
Base58 Class
"""
class Base58(object) :
    def __init__(self,data,prefix=PREFIX) :
        self._prefix = prefix
        if all(c in string.hexdigits for c in data) :
            self._hex     = data
        elif data[0] == "5" or data[0] == "6" :
            self._hex     = base58CheckDecode(data)
        elif data[:len(PREFIX)] == self._prefix :
            self._hex     = btsBase58CheckDecode(data[len(PREFIX):])
        else :
            raise Exception("Error loading Base58 object")
    """
    Format output according to argument _format (wif,btc,bts)
    """
    def __format__(self, _format) :
        if _format.lower() == "wif" :
            return base58CheckEncode(0x80, self._hex)
        elif _format.lower() == "btc":
            return base58CheckEncode(0x00, self._hex)
        elif _format.lower() == "bts" :
            return _format + str(self)
        else :
            raise Exception("Format %s unkown." %_format)
    """
    Returns hex value of object
    """
    def __repr__(self) :
        return self._hex
    """
    Return BTS-base58CheckEncoded string of data
    """
    def __str__(self) :
        return btsBase58CheckEncode(self._hex)
    """
    Return raw bytes
    """
    def __bytes__(self) :
        return unhexlify(self._hex)

# https://github.com/tochev/python3-cryptocoins/raw/master/cryptocoins/base58.py
BASE58_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def base58decode(base58_str):
    base58_text = bytes(base58_str, "ascii")
    n = 0
    leading_zeroes_count = 0
    for b in base58_text:
        n = n * 58 + BASE58_ALPHABET.find(b)
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 256:
        div, mod = divmod(n, 256)
        res.insert(0, mod)
        n = div
    else:
        res.insert(0, n)
    return hexlify(bytearray(1)*leading_zeroes_count + res).decode('ascii')

def base58encode(hexstring):
    byteseq = bytes(unhexlify(bytes(hexstring,'ascii')))
    n = 0
    leading_zeroes_count = 0
    for c in byteseq:
        n = n * 256 + c
        if n == 0:
            leading_zeroes_count += 1
    res = bytearray()
    while n >= 58:
        div, mod = divmod(n, 58)
        res.insert(0, BASE58_ALPHABET[mod])
        n = div
    else:
        res.insert(0, BASE58_ALPHABET[n])
    return (BASE58_ALPHABET[0:1] * leading_zeroes_count + res).decode('ascii')

def ripemd160(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(unhexlify(s))
    return ripemd160.digest()

def doublesha256(s):
    return hashlib.sha256(hashlib.sha256(unhexlify(s)).digest()).digest()

def b58encode(v) :
    return base58encode(v)

def b58decode(v) :
    return base58decode(v)

def base58CheckEncode(version, payload):
    s = ('%.2x'%version) + payload
    checksum = doublesha256(s)[:4]
    result = s + hexlify(checksum).decode('ascii')
    return base58encode(result)

def base58CheckDecode(s):
    s   = unhexlify( base58decode(s) )
    dec = hexlify(s[:-4]).decode('ascii')
    checksum = doublesha256(dec)[:4]
    assert(s[-4:] == checksum)
    return dec[2:]

def btsBase58CheckEncode(s):
    checksum = ripemd160(s)[:4]
    result = s + hexlify(checksum).decode('ascii')
    return base58encode(result)

def btsBase58CheckDecode(s):
    s   = unhexlify( base58decode(s) )
    dec = hexlify(s[:-4]).decode('ascii')
    checksum = ripemd160(dec)[:4]
    assert(s[-4:] == checksum)
    return dec

class Testcases(unittest.TestCase) :
    def test_base58decode(self):
        self.assertEqual([   base58decode('5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'),
                             base58decode('5KYZdUEo39z3FPrtuX2QbbwGnNP5zTd7yyr2SC1j299sBCnWjss'),
                             base58decode('5KfazyjBBtR2YeHjNqX5D6MXvqTUd2iZmWusrdDSUqoykTyWQZB')],
                         [   '800c28fca386c7a227600b2fe50b7cae11ec86d3bf1fbe471be89827e19d72aa1d507a5b8d',
                             '80e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555c5bbb26',
                             '80f3a375e00cc5147f30bee97bb5d54b31a12eee148a1ac31ac9edc4ecd13bc1f80cc8148e'])
    def test_base58encode(self):
        self.assertEqual([   '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ',
                             '5KYZdUEo39z3FPrtuX2QbbwGnNP5zTd7yyr2SC1j299sBCnWjss',
                             '5KfazyjBBtR2YeHjNqX5D6MXvqTUd2iZmWusrdDSUqoykTyWQZB'],
                         [   base58encode('800c28fca386c7a227600b2fe50b7cae11ec86d3bf1fbe471be89827e19d72aa1d507a5b8d'),
                             base58encode('80e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555c5bbb26'),
                             base58encode('80f3a375e00cc5147f30bee97bb5d54b31a12eee148a1ac31ac9edc4ecd13bc1f80cc8148e')])
    def test_btsBase58CheckEncode(self):
        self.assertEqual( [   btsBase58CheckEncode("02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680"),
                              btsBase58CheckEncode("021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16"),
                              btsBase58CheckEncode("02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a"),
                              btsBase58CheckEncode("03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3"),],
                            [ "6dumtt9swxCqwdPZBGXh9YmHoEjFFnNfwHaTqRbQTghGAY2gRz",
                              "5725vivYpuFWbeyTifZ5KevnHyqXCi5hwHbNU9cYz1FHbFXCxX",
                              "6kZKHSuxqAwdCYsMvwTcipoTsNE2jmEUNBQufGYywpniBKXWZK",
                              "8b82mpnH8YX1E9RHnU2a2YgLTZ8ooevEGP9N15c1yFqhoBvJur" ])
    def test_btsBase58CheckDecode(self):
        self.assertEqual( [   "02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680",
                              "021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16",
                              "02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a",
                              "03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3",],
                            [ btsBase58CheckDecode("6dumtt9swxCqwdPZBGXh9YmHoEjFFnNfwHaTqRbQTghGAY2gRz"),
                              btsBase58CheckDecode("5725vivYpuFWbeyTifZ5KevnHyqXCi5hwHbNU9cYz1FHbFXCxX"),
                              btsBase58CheckDecode("6kZKHSuxqAwdCYsMvwTcipoTsNE2jmEUNBQufGYywpniBKXWZK"),
                              btsBase58CheckDecode("8b82mpnH8YX1E9RHnU2a2YgLTZ8ooevEGP9N15c1yFqhoBvJur") ])
    def test_btsb58(self):
        self.assertEqual( [   "02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680",
                              "03457298c4b2c56a8d572c051ca3109dabfe360beb144738180d6c964068ea3e58",
                              "021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16",
                              "02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a",
                              "03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3"],
                            [ btsBase58CheckDecode(btsBase58CheckEncode("02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680")),
                              btsBase58CheckDecode(btsBase58CheckEncode("03457298c4b2c56a8d572c051ca3109dabfe360beb144738180d6c964068ea3e58")),
                              btsBase58CheckDecode(btsBase58CheckEncode("021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16")),
                              btsBase58CheckDecode(btsBase58CheckEncode("02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a")),
                              btsBase58CheckDecode(btsBase58CheckEncode("03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3"))])
    def test_Base58CheckDecode(self):
        self.assertEqual( [   "02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680",
                              "021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16",
                              "02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a",
                              "03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3",
                              "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49",
                              "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131",
                              "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e",
                              "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e",
                              "b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8",
                              ], [ 
                              base58CheckDecode("KwKM6S22ZZDYw5dxBFhaRyFtcuWjaoxqDDfyCcBYSevnjdfm9Cjo"),
                              base58CheckDecode("KwHpCk3sLE6VykHymAEyTMRznQ1Uh5ukvFfyDWpGToT7Hf5jzrie"),
                              base58CheckDecode("KwKTjyQbKe6mfrtsf4TFMtqAf5as5bSp526s341PQEQvq5ZzEo5W"),
                              base58CheckDecode("KwMJJgtyBxQ9FEvUCzJmvr8tXxB3zNWhkn14mWMCTGSMt5GwGLgz"),
                              base58CheckDecode("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"),
                              base58CheckDecode("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S"),
                              base58CheckDecode("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"),
                              base58CheckDecode("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"),
                              base58CheckDecode("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"),
                              ])
    def test_base58CheckEncodeDecopde(self):
        self.assertEqual( [   "02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680",
                              "03457298c4b2c56a8d572c051ca3109dabfe360beb144738180d6c964068ea3e58",
                              "021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16",
                              "02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a",
                              "03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3"],
                            [ base58CheckDecode(base58CheckEncode(0x80,"02e649f63f8e8121345fd7f47d0d185a3ccaa843115cd2e9392dcd9b82263bc680")),
                              base58CheckDecode(base58CheckEncode(0x80,"03457298c4b2c56a8d572c051ca3109dabfe360beb144738180d6c964068ea3e58")),
                              base58CheckDecode(base58CheckEncode(0x80,"021c7359cd885c0e319924d97e3980206ad64387aff54908241125b3a88b55ca16")),
                              base58CheckDecode(base58CheckEncode(0x80,"02f561e0b57a552df3fa1df2d87a906b7a9fc33a83d5d15fa68a644ecb0806b49a")),
                              base58CheckDecode(base58CheckEncode(0x80,"03e7595c3e6b58f907bee951dc29796f3757307e700ecf3d09307a0cc4a564eba3"))])

    def test_Base58(self) :
        self.assertEqual( [   
                              format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"),"wif"),
                              format(Base58("5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"),"wif"),
                              format(Base58("0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"),"wif"),
                              format(Base58("6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"),"wif"),
                              format(Base58("b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"),"wif"),
                              ], [ 
                              "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",
                              "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S",
                              "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                              "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                              "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                              ])

if __name__ == "__main__":
    unittest.main()
