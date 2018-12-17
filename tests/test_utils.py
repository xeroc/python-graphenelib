# -*- coding: utf-8 -*-
import unittest

from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from .fixtures import utils


class Testcases(unittest.TestCase):
    def test_formatTime(self):
        self.assertEqual(utils.formatTime(2000000000), "2033-05-18T03:33:20")

        self.assertEqual(
            utils.formatTime(datetime(2033, 5, 18, 3, 33, 20)), "2033-05-18T03:33:20"
        )

        self.assertEqual(
            utils.formatTimeString(datetime(2033, 5, 18, 3, 33, 20)),
            "2033-05-18T03:33:20",
        )

        with self.assertRaises(ValueError):
            utils.formatTime("empty"),

    def test_formatTimeFromNow(self):
        for i in [1, 30]:
            x = utils.formatTimeFromNow(i)
            now = datetime.utcnow()
            self.assertGreaterEqual(parse(x), now)
            self.assertLessEqual(parse(x), now + timedelta(seconds=i))

    def test_parse(self):
        self.assertEqual(
            datetime(2033, 5, 18, 3, 33, 20, tzinfo=timezone.utc),
            utils.parse_time("2033-05-18T03:33:20"),
        )
