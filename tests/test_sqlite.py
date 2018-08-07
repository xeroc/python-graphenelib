import os
import unittest

from graphenestorage.sqlite import SQLiteStore


class MyStore(SQLiteStore):
    __tablename__ = "testing"
    __key__ = "key"
    __value__ = "value"

    defaults = {"default": "value"}


class Testcases(unittest.TestCase):

    def test_init(self):
        store = MyStore()
        self.assertEqual(store.storageDatabase, "graphene.sqlite")
        store = MyStore(profile="testing")
        self.assertEqual(store.storageDatabase, "testing.sqlite")

        MyStore.data_dir = "/tmp/temporaryFolder"
        store = MyStore(profile="testing")
        self.assertEqual(store.sqlDataBaseFile, "/tmp/temporaryFolder/testing.sqlite")

    def test_initialdata(self):
        store = MyStore()
        store["foobar"] = "banana"
        self.assertEqual(store["foobar"], "banana")

        self.assertIsNone(store["empty"])

        self.assertEqual(store["default"], "value")
        self.assertEqual(len(store), 1)
