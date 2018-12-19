# -*- coding: utf-8 -*-
import unittest
from .fixtures import PrivateKey, encrypt, decrypt


class Testcases(unittest.TestCase):
    def test_loading_encrypted_key(self):

        PrivateKey("42c08720c6d0ce2ab2d7c7398d9e2aad3724dbe3588008676081a15d62e0bcb8")

        with self.assertRaises(Exception):
            PrivateKey("6PRQdSDAjq41FVc58T1gykbihNPQeUCMWj8KW9uoeDKd1ZdZ6MbShYPhvS")
