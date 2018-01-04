import unittest
from graphenebase.ecdsa import (
    sign_message,
    verify_message
)


wif = "5J4KCbg1G3my9b9hCaQXnHSm6vrwW9xQTJS6ZciW2Kek7cCkCEk"


class Testcases(unittest.TestCase):

    def test_sign_message(self):
        signature = sign_message("Foobar", wif)
        self.assertTrue(verify_message("Foobar", signature))
