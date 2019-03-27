# -*- coding: utf-8 -*-
import unittest
from .fixtures import ops, operations, getOperationNameForId, getOperationName


class Testcases(unittest.TestCase):
    def test_ops(self):
        self.assertIsInstance(ops, list)

    def test_operations(self):
        for op, id in operations.items():
            self.assertIsInstance(op, str)
            self.assertIsInstance(id, int)

    def test_getOperationNameForId(self):
        self.assertEqual(getOperationNameForId(0), "demooepration")

        with self.assertRaises(ValueError):
            getOperationNameForId(20)

    def test_operation_type_decode(self):
        self.assertEqual(getOperationName(0), "demooepration")
        self.assertEqual(getOperationName("account_create"), "account_create")
        with self.assertRaises(AssertionError):
            self.assertEqual(getOperationName("-not-exist-"), "account_create")
