import pytest
import unittest
from binascii import hexlify
from graphenebase.account import PrivateKey
import graphenebase.ecdsa as ecdsa


wif = "5J4KCbg1G3my9b9hCaQXnHSm6vrwW9xQTJS6ZciW2Kek7cCkCEk"
pub_key = repr(PrivateKey(wif).pubkey)


class Testcases(unittest.TestCase):

    # Ignore warning:
    # https://www.reddit.com/r/joinmarket/comments/5crhfh/userwarning_implicit_cast_from_char_to_a/
    @pytest.mark.filterwarnings()
    def test_sign_message(self):
        signature = ecdsa.sign_message("Foobar", wif)
        pub_key_sig = ecdsa.verify_message("Foobar", signature)
        self.assertEqual(hexlify(pub_key_sig).decode("latin"), pub_key)

    def test_sign_message_cryptography(self):
        if not ecdsa.CRYPTOGRAPHY_AVAILABLE:
            return
        ecdsa.SECP256K1_MODULE = "cryptography"
        signature = ecdsa.sign_message("Foobar", wif)
        pub_key_sig = ecdsa.verify_message("Foobar", signature)
        self.assertEqual(hexlify(pub_key_sig).decode("latin"), pub_key)

    def test_sign_message_secp256k1(self):
        if not ecdsa.SECP256K1_AVAILABLE:
            return
        ecdsa.SECP256K1_MODULE = "secp256k1"
        signature = ecdsa.sign_message("Foobar", wif)
        pub_key_sig = ecdsa.verify_message("Foobar", signature)
        self.assertEqual(hexlify(pub_key_sig).decode("latin"), pub_key)


if __name__ == '__main__':
    unittest.main()
