import pytest
import unittest
from binascii import hexlify, unhexlify
from graphenebase.account import PrivateKey, PublicKey
from graphenebase.types import (
    Uint32, Int64, String, Bytes,
    Optional, ObjectId
)


wif = "5J4KCbg1G3my9b9hCaQXnHSm6vrwW9xQTJS6ZciW2Kek7cCkCEk"
pub_key = str(PrivateKey(wif).pubkey)

class Testcases(unittest.TestCase):

    def test_read_pubkey(self):
        w = bytes( PublicKey(pub_key) )
        r, b = PublicKey._readwire(w)
        self.assertEqual(str(r), pub_key)

    def test_read_uint32(self):
        v = 256
        w = bytes( Uint32( v ) )
        r, b = Uint32._readwire(w)
        self.assertEqual(r.data, v)

    def test_read_int64(self):
        v = -23
        w = bytes( Int64( v ) )
        r, b = Int64._readwire(w)
        self.assertEqual(r.data, v)

    def test_read_string(self):
        v = "hello world"
        w = bytes( String( v ) )
        r, b = String._readwire(w)
        self.assertEqual(r.data.decode('utf-8'), v)

    def test_read_bytes(self):
        v = "040810172A"
        w = bytes( Bytes( v ) )
        r, b = Bytes._readwire(w)
        self.assertEqual(r.data, unhexlify(v))

    def test_read_objectid(self):
        v = "1.2.0"
        w = bytes( ObjectId( v ) )
        r, b = ObjectId._readwire(w)
        self.assertEqual(r.Id, v)

    def test_read_optional_none(self):
        v = None
        w = bytes( Optional( None ) )
        r, b = Optional._readwire(w, String)
        self.assertEqual(r.data, v)

    def test_read_optional_string(self):
        v = "hello world"
        w = bytes( Optional( String( v ) ) )
        r, b = Optional._readwire(w, String)
        r = r.data
        self.assertEqual(r.data.decode('utf-8'), v)



if __name__ == '__main__':
    unittest.main()