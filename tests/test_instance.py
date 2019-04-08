# -*- coding: utf-8 -*-
import unittest
from .fixtures import (
    fixture_data,
    Chain,
    SharedInstance,
    shared_blockchain_instance,
    set_shared_blockchain_instance,
    set_shared_config,
)


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_shared_instance(self):
        self.assertFalse(SharedInstance.instance)
        c = Chain()
        set_shared_blockchain_instance(c)
        self.assertEqual(id(c), id(SharedInstance.instance))
        c2 = Chain()
        set_shared_blockchain_instance(c2)
        self.assertEqual(id(c2), id(SharedInstance.instance))

    def test_shared_config(self):
        self.assertFalse(SharedInstance.config)
        c = Chain()
        set_shared_config(dict(nobroadcast=True))
        self.assertTrue(SharedInstance.config.get("nobroadcast", False))

        set_shared_blockchain_instance(c)
        set_shared_config(dict(nobroadcast=False))
        self.assertFalse(SharedInstance.config.get("nobroadcast", True))
