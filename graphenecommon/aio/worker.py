# -*- coding: utf-8 -*-
from ..exceptions import WorkerDoesNotExistsException
from ..utils import formatTimeString
from .blockchainobject import BlockchainObject, BlockchainObjects
from ..worker import Worker as SyncWorker, Workers as SyncWorkers


class Worker(BlockchainObject, SyncWorker):
    """ Read data about a worker in the chain

        :param str id: id of the worker
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.type_id
        await BlockchainObject.__init__(self, *args, **kwargs)
        self.post_format()

    async def refresh(self):
        worker = await self.blockchain.rpc.get_object(self.identifier)
        if not worker:
            raise WorkerDoesNotExistsException
        await super(Worker, self).__init__(worker, blockchain_instance=self.blockchain)
        self.post_format()

    @property
    async def account(self):
        return await self.account_class(
            self["worker_account"], blockchain_instance=self.blockchain
        )


class Workers(BlockchainObjects, SyncWorkers):
    """ Obtain a list of workers for an account

        :param str account_name/id: Name/id of the account (optional)
        :param instance blockchain_instance: instance to use when accesing a RPC
    """

    async def __init__(self, *args, account_name=None, lazy=False, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.worker_class

        self.account_name = account_name
        self.lazy = lazy
        await super().__init__(*args, **kwargs)

    async def refresh(self, *args, **kwargs):
        if self.account_name:
            account = await self.account_class(
                self.account_name, blockchain_instance=self.blockchain
            )
            self.workers = await self.blockchain.rpc.get_workers_by_account(
                account["id"]
            )
        else:
            self.workers = await self.blockchain.rpc.get_all_workers()

        self.store(
            [
                await self.worker_class(
                    x, lazy=self.lazy, blockchain_instance=self.blockchain
                )
                for x in self.workers
            ]
        )
