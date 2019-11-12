# -*- coding: utf-8 -*-
import json
import aiounittest
from .fixtures_aio import fixture_data, Message, MessageV1, MessageV2
from pprint import pprint
from graphenecommon.exceptions import InvalidMessageSignature


class Testcases(aiounittest.AsyncTestCase):
    def setUp(self):
        fixture_data()

    async def test_sign_message(self):
        m = await Message("message foobar")
        p = await m.sign(account="init0")
        m2 = await Message(p)
        await m2.verify()

    async def test_verify_message(self):
        m = await Message(
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
        )
        await m.verify()

        with self.assertRaises(InvalidMessageSignature):
            m = await Message(
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
            )
            await m.verify()

    async def test_v2_enc(self):
        m = await MessageV2("foobar")
        c = await m.sign(account="init0")
        v = await MessageV2(c)
        await v.verify()

    async def test_v2_enc_string(self):
        m = await MessageV2("foobar")
        c = await m.sign(account="init0")
        v = await MessageV2(json.dumps(c))
        await v.verify()

    async def test_v2andv1_enc(self):
        m = await MessageV2("foobar")
        c = await m.sign(account="init0")
        v = await Message(c)
        await v.verify()

        m = await MessageV1("foobar")
        c = await m.sign(account="init0")
        v = await Message(c)
        await v.verify()
