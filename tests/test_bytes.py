import pytest
import unittest
from binascii import hexlify, unhexlify
from graphenebase.account import PrivateKey, PublicKey
from graphenebase.types import (
    Uint32, Int64, String, Bytes,
    Fixed_Bytes,
    Optional, ObjectId
)


wif = "5J4KCbg1G3my9b9hCaQXnHSm6vrwW9xQTJS6ZciW2Kek7cCkCEk"
pub_key = str(PrivateKey(wif).pubkey)

class Testcases(unittest.TestCase):

    def test_read_pubkey(self):
        w = bytes( PublicKey(pub_key) )
        r, b = PublicKey.fromBytes(w)
        self.assertEqual(str(r), pub_key)

    def test_read_uint32(self):
        v = 256
        w = bytes( Uint32( v ) )
        r, b = Uint32.fromBytes(w)
        self.assertEqual(r.data, v)

    def test_read_int64(self):
        v = -23
        w = bytes( Int64( v ) )
        r, b = Int64.fromBytes(w)
        self.assertEqual(r.data, v)

    def test_read_string(self):
        v = "hello world"
        w = bytes( String( v ) )
        r, b = String.fromBytes(w)
        self.assertEqual(r.data.decode('utf-8'), v)

    def test_read_bytes(self):
        v = "040810172A"
        w = bytes( Bytes( v ) )
        r, b = Bytes.fromBytes(w)
        self.assertEqual(r.data, unhexlify(v))

    def test_read_fixedbytes(self):
        v = "0408"
        w = bytes( Fixed_Bytes( v, 4 ) )
        r, b = Fixed_Bytes.fromBytes(w, 4)
        self.assertEqual(r.data, unhexlify(v))

    def test_read_objectid(self):
        v = "1.2.0"
        w = bytes( ObjectId( v ) )
        r, b = ObjectId.fromBytes(w)
        self.assertEqual(r.Id, v)

    def test_read_optional_none(self):
        v = None
        w = bytes( Optional( None ) )
        r, b = Optional.fromBytes(w, String)
        self.assertEqual(r.data, v)

    def test_read_optional_string(self):
        v = "hello world"
        w = bytes( Optional( String( v ) ) )
        r, b = Optional.fromBytes(w, String)
        r = r.data
        self.assertEqual(r.data.decode('utf-8'), v)



if __name__ == '__main__':
    unittest.main()
