# -*- coding: utf-8 -*-
import json
import unittest
from .fixtures import fixture_data, Message, MessageV1, MessageV2
from pprint import pprint
from graphenecommon.exceptions import InvalidMessageSignature


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_sign_message(self):
        p = Message("message foobar").sign(account="init0")
        Message(p).verify()

    def test_verify_message(self):
        Message(
            """
-----BEGIN GRAPHENE SIGNED MESSAGE-----
message foobar
-----BEGIN META-----
account=init0
memokey=GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV
block=33041174
timestamp=2018-12-12T10:44:15
-----BEGIN SIGNATURE-----
1f3745b4bf1a835623698a94fafea35fa654b7a554cdde4f4f591d6acc2a5f5cec664ce4d18ddf26495ecf12ee701e7321c12c178c8e1d248d5c3d794c658e4a8b
-----END GRAPHENE SIGNED MESSAGE-----"""
        ).verify()

        with self.assertRaises(InvalidMessageSignature):
            Message(
                "-----BEGIN GRAPHENE SIGNED MESSAGE-----"
                "message foobar\n"
                "-----BEGIN META-----"
                "account=init0\n"
                "memokey=GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV\n"
                "block=23814223\n"
                "timestamp=2018-01-24T11:42:33"
                "-----BEGIN SIGNATURE-----"
                "2034f601e175a25cf9f60a828650301f57c9efab53929b6a82fb413feb8a786fcb3ba4238dd8bece03aee38526ee363324d43944d4a3f9dc624fbe53ef5f0c9a5e\n"
                "-----END GRAPHENE SIGNED MESSAGE-----"
            ).verify()

    def test_v2_enc(self):
        m = MessageV2("foobar")
        c = m.sign(account="init0")
        v = MessageV2(c)
        v.verify()

    def test_v2_enc_string(self):
        m = MessageV2("foobar")
        c = m.sign(account="init0")
        v = MessageV2(json.dumps(c))
        v.verify()

    def test_v2andv1_enc(self):
        m = MessageV2("foobar")
        c = m.sign(account="init0")
        v = Message(c)
        v.verify()

        m = MessageV1("foobar")
        c = m.sign(account="init0")
        v = Message(c)
        v.verify()
