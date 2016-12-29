import sys
import threading
import websocket
import ssl
# from websocket._exceptions import WebSocketConnectionClosedException
import json
import time
from itertools import cycle
import logging
log = logging.getLogger(__name__)


class RPCError(Exception):
    pass


class NumRetriesReached(Exception):
    pass


class GrapheneWebsocketRPC(object):
    """ This class allows to call API methods synchronously, without
        callbacks. It logs in and registers to the APIs:

        * database
        * history

        :param str urls: Either a single Websocket URL, or a list of URLs
        :param str user: Username for Authentication
        :param str password: Password for Authentication
        :param Array apis: List of APIs to register to (default: ["database", "network_broadcast"])
        :param int num_retries: Try x times to num_retries to a node on disconnect, -1 for indefinitely

        Available APIs

              * database
              * network_node
              * network_broadcast
              * history

        Usage:

        .. code-block:: python

            ws = GrapheneWebsocketRPC("ws://10.0.0.16:8090","","")
            print(ws.get_account_count())

        .. note:: This class allows to call methods available via
                  websocket. If you want to use the notification
                  subsystem, please use ``GrapheneWebsocket`` instead.

    """
    def __init__(self, urls, user="", password="", **kwargs):
        self.api_id = {}
        self._request_id = 0
        if isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])
        self.user = user
        self.password = password
        self.num_retries = kwargs.get("num_retries", -1)

        self.wsconnect()
        self.register_apis()

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    def wsconnect(self):
        cnt = 0
        while True:
            cnt += 1
            self.url = next(self.urls)
            log.debug("Trying to connect to node %s" % self.url)
            if self.url[:3] == "wss":
                sslopt_ca_certs = {'cert_reqs': ssl.CERT_NONE}
                self.ws = websocket.WebSocket(sslopt=sslopt_ca_certs)
            else:
                self.ws = websocket.WebSocket()
            try:
                self.ws.connect(self.url)
                break
            except KeyboardInterrupt:
                raise
            except:
                if (self.num_retries >= 0 and cnt > self.num_retries):
                    raise NumRetriesReached()

                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during wsconnect(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries) +
                        "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)
        self.login(self.user, self.password, api_id=1)

    def register_apis(self):
        self.api_id["database"] = self.database(api_id=1)
        self.api_id["history"] = self.history(api_id=1)
        self.api_id["network_broadcast"] = self.network_broadcast(api_id=1)

    def get_account(self, name, **kwargs):
        """ Get full account details from account name or id

            :param str name: Account name or account id
        """
        if len(name.split(".")) == 3:
            return self.get_objects([name])[0]
        else :
            return self.get_account_by_name(name, **kwargs)

    def get_asset(self, name, **kwargs):
        """ Get full asset from name of id

            :param str name: Symbol name or asset id (e.g. 1.3.0)
        """
        if len(name.split(".")) == 3:
            return self.get_objects([name], **kwargs)[0]
        else :
            return self.lookup_asset_symbols([name], **kwargs)[0]

    def get_object(self, o, **kwargs):
        """ Get object with id ``o``

            :param str o: Full object id
        """
        return self.get_objects([o], **kwargs)[0]

    def loop_account_history(self, account, start=0, only_ops=[]):
        """ Returns a generator for individual account transactions

            :param str account: account name to get history for
            :param int start: sequence number of the first transaction to return
            :param array only_ops: Limit generator by these operations (ids)
        """
        account = self.get_account(account)
        cnt = 0
        while True:
            ret = self.get_relative_account_history(
                account["id"],
                start,
                100,
                start + 101,
                api="history",
            )[::-1]
            for i in ret:
                if not only_ops or i["op"][0] in only_ops:
                    cnt += 1
                    yield i
            if len(ret) < 100:
                break

            start += 100

    def getFullAccountHistory(self, account, begin=1, limit=100, sort="block", **kwargs):
        """ Get History of an account

            :param string account: account name or account id
            :param number begin: sequence number of first element
            :param number limit: limit number of entries
            :param string sort: Either "block" or "reversed"


            **Example:**

            The following code will give you you the first 110
            operations for the account ``faucet`` starting at the first
            operation:

            .. code-block:: python

                client = GrapheneClient(config)
                client.ws.getAccountHistory(
                    "faucet",
                    begin=1,
                    limit=110,
                )

        """
        if account[0:4] == "1.2." :
            account_id = account
        else:
            account_id = self.get_account_by_name(account, **kwargs)["id"]

        if begin < 1:
            raise ValueError("begin cannot be smaller than 1")

        if sort != "block":
            raise Exception("'sort' can currently only be 'block' " +
                            "due to backend API issues")

        r = []
        if limit <= 100:
            if sort == "block":
                ret = self.get_relative_account_history(
                    account_id,
                    begin,
                    limit,
                    begin + limit,
                    api="history", **kwargs
                )
                [r.append(a) for a in ret[::-1]]
            else:
                ret = self.get_relative_account_history(
                    account_id,
                    begin,
                    limit,
                    0,
                    api="history"
                )
                [r.append(a) for a in ret]
        else :
            while True:

                if len(r) + 100 > limit:
                    thislimit = limit - len(r)
                else:
                    thislimit = 100

                if sort == "block":
                    ret = self.get_relative_account_history(
                        account_id,
                        begin,
                        thislimit,
                        begin + thislimit,
                        api="history", **kwargs
                    )
                    [r.append(a) for a in ret[::-1]]
                    begin += thislimit
                else:
                    ret = self.get_relative_account_history(
                        account_id,
                        begin,
                        thislimit,
                        0,
                        api="history", **kwargs
                    )
                    [r.append(a) for a in ret]

                if len(ret) < 100 :
                    break

        return r

    """ Block Streams
    """
    def block_stream(self, start=None, mode="irreversible", **kwargs):
        """ Yields blocks starting from ``start``.

            :param int start: Starting block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        # Let's find out how often blocks are generated!
        config = self.get_global_properties(**kwargs)
        block_interval = config["parameters"]["block_interval"]

        if not start:
            props = self.get_dynamic_global_properties(**kwargs)
            # Get block number
            if mode == "head":
                start = props['head_block_number']
            elif mode == "irreversible":
                start = props['last_irreversible_block_num']
            else:
                raise ValueError(
                    '"mode" has to be "head" or "irreversible"'
                )

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            # head/last reversible block
            props = self.get_dynamic_global_properties(**kwargs)

            # Get block number
            if mode == "head":
                head_block = props['head_block_number']
            elif mode == "irreversible":
                head_block = props['last_irreversible_block_num']
            else:
                raise ValueError(
                    '"mode" has to be "head" or "irreversible"'
                )

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                yield self.get_block(blocknum, **kwargs)

            # Set new start
            start = head_block + 1

            # Sleep for one block
            time.sleep(block_interval)

    def stream(self, opName, *args, **kwargs):
        """ Yield specific operations (e.g. transfers) only

            :param str opName: Name of the operation, e.g.  transfer,
                limit_order_create, limit_order_cancel, call_order_update,
                fill_order, account_create, account_update,
                account_whitelist, account_upgrade, account_transfer,
                asset_create, asset_update, asset_update_bitasset,
                asset_update_feed_producers, asset_issue, asset_reserve,
                asset_fund_fee_pool, asset_settle, asset_global_settle,
                asset_publish_feed, witness_create, witness_update,
                proposal_create, proposal_update, proposal_delete,
                withdraw_permission_create, withdraw_permission_update,
                withdraw_permission_claim, withdraw_permission_delete,
                committee_member_create, committee_member_update,
                committee_member_update_global_parameters,
                vesting_balance_create, vesting_balance_withdraw,
                worker_create, custom, assert, balance_claim,
                override_transfer, transfer_to_blind, blind_transfer,
                transfer_from_blind, asset_settle_cancel, asset_claim_fees
            :param int start: Begin at this block
        """
        from graphenebase.operations import getOperationNameForId
        for block in self.block_stream(*args, **kwargs):
            if not len(block["transactions"]):
                continue
            for tx in block["transactions"]:
                for op in tx["operations"]:
                    if getOperationNameForId(op[0]) == opName:
                        yield op[1]

    """ RPC Calls
    """
    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON format
            :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))
        cnt = 0
        while True:
            cnt += 1

            try:
                self.ws.send(json.dumps(payload, ensure_ascii=False).encode('utf8'))
                reply = self.ws.recv()
                break
            except KeyboardInterrupt:
                raise
            except:
                if (self.num_retries > -1 and
                        cnt > self.num_retries):
                    raise NumRetriesReached()
                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during rpcexec(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries) +
                        "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)

                # retry
                try:
                    self.ws.close()
                    time.sleep(sleeptime)
                    self.wsconnect()
                    self.register_apis()
                except:
                    pass

        ret = {}
        try:
            ret = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")

        log.debug(json.dumps(reply))

        if 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            return ret["result"]

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs :
                if ("api" in kwargs):
                    if (kwargs["api"] in self.api_id and
                            self.api_id[kwargs["api"]]):
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        raise ValueError(
                            "Unknown API! "
                            "Verify that you have registered to %s"
                            % kwargs["api"]
                        )
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {"method": "call",
                     "params": [api_id, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": self.get_request_id()}
            r = self.rpcexec(query)
            return r
        return method
