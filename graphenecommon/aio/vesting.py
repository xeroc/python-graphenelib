# -*- coding: utf-8 -*-
from ..exceptions import VestingBalanceDoesNotExistsException
from .blockchainobject import BlockchainObject
from ..vesting import Vesting as SyncVesting


class Vesting(BlockchainObject, SyncVesting):
    """ Read data about a Vesting Balance in the chain

        :param str id: Id of the vesting balance
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.type_id
        assert self.amount_class
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        result = await self.blockchain.rpc.get_objects([self.identifier])
        obj = result[0]
        if not obj:
            raise VestingBalanceDoesNotExistsException
        await super(Vesting, self).__init__(obj, blockchain_instance=self.blockchain)

    @property
    async def account(self):
        return await self.account_class(
            self["owner"], blockchain_instance=self.blockchain
        )

    @property
    async def claimable(self):
        if self["policy"][0] == 1:
            p = self["policy"][1]
            ratio = (
                (
                    (float(p["coin_seconds_earned"]) / float(self["balance"]["amount"]))
                    / float(p["vesting_seconds"])
                )
                if float(p["vesting_seconds"]) > 0.0
                and float(self["balance"]["amount"])
                else 1
            )
            return (
                await self.amount_class(
                    self["balance"], blockchain_instance=self.blockchain
                )
                * ratio
            )
        elif self["policy"][0] == 2:
            return await self.amount_class(
                self["balance"], blockchain_instance=self.blockchain
            )
        else:
            raise NotImplementedError("This policy isn't implemented yet")

    async def claim(self, amount=None):
        assert callable(self.blockchain.vesting_balance_withdraw)
        return await self.blockchain.vesting_balance_withdraw(
            self["id"], amount=amount, account=self["owner"]
        )
