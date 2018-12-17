# -*- coding: utf-8 -*-
import unittest
from .fixtures import PublicKey


class Testcases(unittest.TestCase):
    def test_order_1(self):
        mylist = [
            PublicKey("GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x"),
            PublicKey("GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp"),
            PublicKey("GPH8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7"),
        ]
        sorted_list = sorted(mylist)
        self.assertEqual(
            [str(x) for x in sorted_list],
            [
                "GPH8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7",
                "GPH6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x",
                "GPH6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp",
            ],
        )
