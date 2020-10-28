# -*- coding: utf-8 -*-
import mock
import time
import unittest
from .fixtures import ObjectCacheInMemory, Account


class Testcases(unittest.TestCase):
    def test_cache(self):
        cache = ObjectCacheInMemory(default_expiration=1)
        self.assertEqual(str(cache), "ObjectCacheInMemory(default_expiration=1)")

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

    def test_max_length_cache(self):
        cache = ObjectCacheInMemory(default_expiration=1, max_length=10)
        self.assertEqual(str(cache), "ObjectCacheInMemory(default_expiration=1)")

        for num in range(0, 10):
            cache[str(num)] = "bar"

        self.assertEqual(len(cache), 10)

        for num in range(11, 50):
            cache[str(num)] = "bar"

        self.assertEqual(len(cache), 10)

    def test_cache_list(self):
        cache = ObjectCacheInMemory(default_expiration=1)
        self.assertEqual(str(cache), "ObjectCacheInMemory(default_expiration=1)")

        # Data
        cache["foo"] = [1, 2, 3, 4, 5, 6]

        self.assertIn("foo", cache)
        self.assertEqual(cache["foo"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(cache.get("foo", "New"), [1, 2, 3, 4, 5, 6])

        # Expiration
        time.sleep(2)
        self.assertNotIn("foo", cache)

        # Get
        self.assertEqual(cache.get("foo", "New"), "New")

    def test_lazy_loading(self):
        a = Account("unittest", lazy=True)
        self.assertFalse(a._fetched)
        self.assertTrue(a._lazy)
        with mock.patch.object(Account, "refresh") as mocked_os:
            try:
                # Should call refresh as we are lazy here and don't have that
                # object cached/fetched
                a["name"]
            except Exception:
                pass
            mocked_os.assert_called_once()
