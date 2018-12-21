# -*- coding: utf-8 -*-
import mock
import time
import unittest
from .fixtures import ObjectCache, Account


class Testcases(unittest.TestCase):
    def test_cache(self):
        cache = ObjectCache(default_expiration=1)
        self.assertEqual(str(cache), "ObjectCache(n=0, default_expiration=1)")

        # Data
        cache["foo"] = "bar"
        self.assertIn("foo", cache)
        self.assertEqual(cache["foo"], "bar")
        self.assertEqual(cache.get("foo", "New"), "bar")

        # Expiration
        time.sleep(2)
        self.assertNotIn("foo", cache)

        # Get
        self.assertEqual(cache.get("foo", "New"), "New")

    def test_lazy_loading(self):
        a = Account("unittest", lazy=True)
        self.assertFalse(a._fetched)
        with mock.patch.object(Account, "refresh") as mocked_os:
            try:
                # Should call refresh as we are lazy here and don't have that
                # object cached/fetched
                a["name"]
            except Exception:
                pass
            mocked_os.assert_called_once()
