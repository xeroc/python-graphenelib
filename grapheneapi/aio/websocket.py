# -*- coding: utf-8 -*-
import asyncio
import websockets
import logging
import json

from .rpc import Rpc
from ..exceptions import RPCError

log = logging.getLogger(__name__)


class Websocket(Rpc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = None
        self.client = None
        self._messages = {}
        self.notifications = asyncio.Queue(loop=self.loop)
        self._event = asyncio.Event(loop=self.loop)

    async def connect(self):
        if log.getEffectiveLevel() == logging.DEBUG:
            logging.getLogger("websockets").setLevel(logging.DEBUG)

        ssl = True if self.url[:3] == "wss" else None
        self.ws = await websockets.connect(self.url, ssl=ssl, loop=self.loop)
        task = self.loop.create_task(self.parse_messages())
        task.add_done_callback(self.handle_parse_stop)

    async def disconnect(self):
        if self.ws:
            await self.ws.close()

    def handle_parse_stop(self, task):
        try:
            task.result()
        except Exception:
            log.exception("Task stopped with exception")
        else:
            log.info("Task stopped with result: {}".format(task.result()))

    async def parse_messages(self):
        """ Listen websocket for incoming messages in infinity manner

            Messages which are responses (has id) are stored in dict, while
            messages which are notifies are stored in asyncio queue and are
            supposed to be processed later by whom who sets the subscribtion
            callback
        """

        async for message in self.ws:
            m = json.loads(message, strict=False)
            if "id" in m:
                log.debug("got mesage id {}".format(m["id"]))
                if m["id"] is None:
                    # Got message with null id
                    try:
                        for entry in m["error"]["data"]["stack"]:
                            # Iterate over all entries in error details
                            try:
                                original_message = json.loads(entry["data"]["str"])
                                m["id"] = original_message["id"]
                            except KeyError:
                                continue
                            else:
                                break
                    except KeyError:
                        pass
                    finally:
                        if not m["id"]:
                            # Fuckup, we was unable to extract original message
                            log.critical(
                                "Got error and unable to match it with proper request"
                            )
                            raise RuntimeError(m)
                        log.debug(
                            "restored message id by parsing node response: {}".format(
                                m["id"]
                            )
                        )
                self._messages[m["id"]] = m
                # Notify waiting coroutines that we have a new response
                self._event.set()
            elif m.get("method") == "notice":
                await self.notifications.put(m)

    async def get_response_by_id(self, request_id):
        """ Pop response from dict containing all query results

            :param int request_id: request id to get response to
        """
        response = None
        while not response:
            # Reset event state
            self._event.clear()
            # Lock until response will be available
            await self._event.wait()
            log.debug("looking for response id {}".format(request_id))
            response = self._messages.pop(request_id, None)
        return response

    async def rpcexec(self, payload):
        """ Execute a RPC call

            :param dict payload: json-rpc request in format:
                {"jsonrpc": "2.0", "method": "call", "params": "[x, y, z]", "id": 1}
        """
        if not self.ws:
            await self.connect()

        request_id = payload["id"]
        request_json = json.dumps(payload)

        await self.ws.send(request_json)
        response = await self.get_response_by_id(request_id)

        return response
