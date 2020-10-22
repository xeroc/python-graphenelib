# -*- coding: utf-8 -*-
import unittest
from .fixtures import Api, Websocket, Http, exceptions

urls = ["wss://eu.nodes.bitshares.ws", "https://eu.nodes.bitshares.ws"]


class Testcases(unittest.TestCase):
    def test_apiInit(self):
        api = Api(urls)
        self.assertEqual(len(api._url_counter), 2)
        api_single = Api(urls[0])
        self.assertEqual(len(api_single._url_counter), 1)

    def test_chain_params(self):
        api = Api(urls)
        p = api.chain_params
        self.assertEqual(p, api.get_network())
        self.assertEqual(
            p.get("chain_id"),
            "4018d7844c78f6a6c41c6a552b898022310fc5dec06da467ee7905a8dad512c8",
        )
        self.assertIsInstance(api.api_id, dict)

    def test_websocket_connection(self):
        api = Api(urls[0])
        self.assertIsInstance(api.connection, Websocket)
        api = Api(urls[1])
        self.assertIsInstance(api.connection, Http)
        with self.assertRaises(ValueError):
            Api("hssp://error.example.com", num_retries=1)

    def test_call(self):
        api = Api(urls[0])
        api.get_objects(["2.8.0"], api="database")

    def test_cconnection_exceptions(self):
        with self.assertRaises(exceptions.NumRetriesReached):
            api = Api("http://error.example.com", num_retries=0)
            api.get_objects(["2.8.0"])
        with self.assertRaises(exceptions.NumRetriesReached):
            api = Api("http://error.example.com", num_retries=1)
            api.get_objects(["2.8.0"])

    def test_raise_rpc_error_wss(self):
        api = Api(urls[0], num_retries=1)
        with self.assertRaises(exceptions.RPCError):
            api.get_SOMETHING(["2.8.0"])
        api.connection.disconnect()
        api.connection.disconnect()

    # def test_raise_rpc_error_https(self):
    #    api = Api(urls[1], num_retries=1)
    #    with self.assertRaises(exceptions.RPCError):
    #        api.get_SOMETHING(["2.8.0"])

    def test_login(self):
        Api(urls[0], "User", "password", num_retries=1)
        Api(urls[0], None, None, num_retries=1)

    def test_rollover(self):
        api = Api(["http://error.example.com", urls[0]])
        api.get_objects(["2.8.0"])
