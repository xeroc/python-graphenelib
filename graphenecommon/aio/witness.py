# -*- coding: utf-8 -*-
from ..exceptions import WitnessDoesNotExistsException
from .blockchainobject import BlockchainObject, BlockchainObjects
from ..witness import Witness as SyncWitness, Witnesses as SyncWitnesses


class Witness(BlockchainObject, SyncWitness):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id or self.type_ids
        assert self.account_class
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 6:
                witness = await self.blockchain.rpc.get_object(self.identifier)
            else:
                witness = await self.blockchain.rpc.get_witness_by_account(
                    self.identifier
                )
        else:
            account = await self.account_class(
                self.identifier, blockchain_instance=self.blockchain
            )
            witness = await self.blockchain.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException(self.identifier)
        await super(Witness, self).__init__(
            witness, blockchain_instance=self.blockchain
        )

    @property
    async def account(self):
        return await self.account_class(
            self["witness_account"], blockchain_instance=self.blockchain
        )

    @property
    async def weight(self):
        if not self.is_active:
            return 0
        else:
            account = await self.account_class(
                "witness-account", blockchain_instance=self.blockchain
            )
            threshold = account["active"]["weight_threshold"]
            weight = next(
                filter(
                    lambda x: x[0] == self.account["id"],
                    account["active"]["account_auths"],
                )
            )
            return float(weight[1]) / float(threshold)

    @property
    async def is_active(self):
        account = await self.account_class(
            "witness-account", blockchain_instance=self.blockchain
        )
        return self.account["id"] in [x[0] for x in account["active"]["account_auths"]]


class Witnesses(BlockchainObjects, SyncWitnesses):
    """ Obtain a list of **active** witnesses and the current schedule

        :param bool only_active: (False) Only return witnesses that are
            actively producing blocks
        :param instance blockchain_instance: instance to use when accesing a RPC
    """

    async def __init__(self, *args, only_active=False, lazy=False, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.witness_class

        self.lazy = lazy
        self.only_active = only_active
        await super().__init__(*args, **kwargs)

    async def refresh(self, *args, **kwargs):
        self.schedule = await self.blockchain.rpc.get_object("2.12.0").get(
            "current_shuffled_witnesses", []
        )

        witnesses = [
            await self.witness_class(
                x, lazy=self.lazy, blockchain_instance=self.blockchain
            )
            for x in self.schedule
        ]

        if self.only_active:
            account = await self.account_class(
                "witness-account", blockchain_instance=self.blockchain
            )
            filter_by = [x[0] for x in account["active"]["account_auths"]]
            witnesses = list(
                filter(lambda x: x["witness_account"] in filter_by, witnesses)
            )

        self.store(witnesses)

    def __contains__(self, item):
        if self.witness_class.objectid_valid(item):
            id = item
        elif isinstance(item, self.account_class):
            id = item["id"]
        else:
            # Async version does not support querying by name
            raise NotImplementedError("Please use object id or Account class")

        return any([id == x["id"] for x in self]) or any(
            [id == x["witness_account"] for x in self]
        )
