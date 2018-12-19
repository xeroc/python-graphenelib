# -*- coding: utf-8 -*-
import unittest
from graphenecommon import exceptions
from .fixtures import fixture_data, Account, Committee


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_Committee(self):
        with self.assertRaises(exceptions.AccountDoesNotExistsException):
            Committee("FOObarNonExisting")

        c = Committee("1.5.0")
        self.assertEqual(c["id"], "1.5.0")
        self.assertIsInstance(c.account, Account)

        with self.assertRaises(exceptions.CommitteeMemberDoesNotExistsException):
            Committee("1.5.1")
