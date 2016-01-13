#!/usr/bin/python

from Crypto.Cipher import AES
import scrypt
import hashlib
from binascii import hexlify, unhexlify
import unittest
import sys
from .account import PrivateKey
from .base58 import Base58, base58decode

""" This class and the methods require python3 """
assert sys.version_info[0] == 3, "graphenelib requires python3"


class SaltException(Exception) :
    pass


def _encrypt_xor(a, b, aes) :
    """ Returns encrypt(a ^ b). """
    a = unhexlify('%0.32x' % (int((a), 16) ^ int(hexlify(b), 16)))
    return aes.encrypt(a)


def encrypt(privkey, passphrase) :
    """ BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.

    :param privkey: Private key
    :type privkey: Base58
    :param str passphrase: UTF-8 encoded passphrase for encryption
    :return: BIP0038 non-ec-multiply encrypted wif key
    :rtype: Base58

    """
    privkeyhex    = repr(privkey)   # hex
    addr          = format(privkey.uncompressed.address, "BTC")
    a             = bytes(addr, 'ascii')
    salt          = hashlib.sha256(hashlib.sha256(a).digest()).digest()[0:4]
    key           = scrypt.hash(passphrase, salt, 16384, 8, 8)
    (derived_half1, derived_half2) = (key[:32], key[32:])
    aes             = AES.new(derived_half2)
    encrypted_half1 = _encrypt_xor(privkeyhex[:32], derived_half1[:16], aes)
    encrypted_half2 = _encrypt_xor(privkeyhex[32:], derived_half1[16:], aes)
    " flag byte is forced 0xc0 because BTS only uses compressed keys "
    payload    = (b'\x01' + b'\x42' + b'\xc0' +
                  salt + encrypted_half1 + encrypted_half2)
    " Checksum "
    checksum   = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    privatkey  = hexlify(payload + checksum).decode('ascii')
    return Base58(privatkey)


def decrypt(encrypted_privkey, passphrase):
    """BIP0038 non-ec-multiply decryption. Returns WIF privkey.

    :param Base58 encrypted_privkey: Private key
    :param str passphrase: UTF-8 encoded passphrase for decryption
    :return: BIP0038 non-ec-multiply decrypted key
    :rtype: Base58
    :raises SaltException: if checksum verification failed (e.g. wrong password)

    """

    d        = unhexlify(base58decode(encrypted_privkey))
    d        = d[2:]   # remove trailing 0x01 and 0x42
    flagbyte = d[0:1]  # get flag byte
    d        = d[1:]   # get payload
    assert flagbyte == b'\xc0', "Flagbyte has to be 0xc0"
    salt     = d[0:4]
    d        = d[4:-4]
    key      = scrypt.hash(passphrase, salt, 16384, 8, 8)
    derivedhalf1   = key[0:32]
    derivedhalf2   = key[32:64]
    encryptedhalf1 = d[0:16]
    encryptedhalf2 = d[16:32]
    aes            = AES.new(derivedhalf2)
    decryptedhalf2 = aes.decrypt(encryptedhalf2)
    decryptedhalf1 = aes.decrypt(encryptedhalf1)
    privraw        = decryptedhalf1 + decryptedhalf2
    privraw        = ('%064x' % (int(hexlify(privraw), 16) ^
                                 int(hexlify(derivedhalf1), 16)))
    wif            = Base58(privraw)
    """ Verify Salt """
    privkey        = PrivateKey(format(wif, "wif"))
    addr           = format(privkey.uncompressed.address, "BTC")
    a              = bytes(addr, 'ascii')
    saltverify     = hashlib.sha256(hashlib.sha256(a).digest()).digest()[0:4]
    if saltverify != salt :
        raise SaltException('checksum verification failed! Password may be incorrect.')
    return wif


class Testcases(unittest.TestCase) :
    def test_encrypt(self):
        self.assertEqual([
                             format(encrypt(PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"), "TestingOneTwoThree"), "encwif"),
                             format(encrypt(PrivateKey("5KN7MzqK5wt2TP1fQCYyHBtDrXdJuXbUzm4A9rKAteGu3Qi5CVR"), "TestingOneTwoThree"), "encwif"),
                             format(encrypt(PrivateKey("5HtasZ6ofTHP6HCwTqTkLDuLQisYPah7aUnSKfC7h4hMUVw2gi5"), "Satoshi"), "encwif"),
                         ],[
                             "6PRN5mjUTtud6fUXbJXezfn6oABoSr6GSLjMbrGXRZxSUcxThxsUW8epQi",
                             "6PRVWUbkzzsbcVac2qwfssoUJAN1Xhrg6bNk8J7Nzm5H7kxEbn2Nh2ZoGg",
                             "6PRNFFkZc2NZ6dJqFfhRoFNMR9Lnyj7dYGrzdgXXVMXcxoKTePPX1dWByq",
                         ])
                    
    def test_deencrypt(self):
        self.assertEqual([
                    format(decrypt("6PRN5mjUTtud6fUXbJXezfn6oABoSr6GSLjMbrGXRZxSUcxThxsUW8epQi","TestingOneTwoThree"),"wif"),
                    format(decrypt("6PRVWUbkzzsbcVac2qwfssoUJAN1Xhrg6bNk8J7Nzm5H7kxEbn2Nh2ZoGg","TestingOneTwoThree"),"wif"),
                    format(decrypt("6PRNFFkZc2NZ6dJqFfhRoFNMR9Lnyj7dYGrzdgXXVMXcxoKTePPX1dWByq","Satoshi"),"wif")
                ],[
                    "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",
                    "5KN7MzqK5wt2TP1fQCYyHBtDrXdJuXbUzm4A9rKAteGu3Qi5CVR",
                    "5HtasZ6ofTHP6HCwTqTkLDuLQisYPah7aUnSKfC7h4hMUVw2gi5",
                ])

if __name__ == '__main__':
    unittest.main()
