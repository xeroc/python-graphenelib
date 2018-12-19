# -*- coding: utf-8 -*-
from .exceptions import VestingBalanceDoesNotExistsException
from .blockchainobject import BlockchainObject
from .instance import AbstractBlockchainInstanceProvider


class Vesting(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ Read data about a Vesting Balance in the chain

        :param str id: Id of the vesting balance
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.type_id
        assert self.amount_class
        BlockchainObject.__init__(self, *args, **kwargs)

    def refresh(self):
        obj = self.blockchain.rpc.get_objects([self.identifier])[0]
        if not obj:
            raise VestingBalanceDoesNotExistsException
        super(Vesting, self).__init__(obj, blockchain_instance=self.blockchain)

    @property
    def account(self):
        return self.account_class(self["owner"], blockchain_instance=self.blockchain)

    @property
    def claimable(self):
        if self["policy"][0] == 1:
            p = self["policy"][1]
            ratio = (
                (
                    (float(p["coin_seconds_earned"]) / float(self["balance"]["amount"]))
                    / float(p["vesting_seconds"])
                )
                if float(p["vesting_seconds"]) > 0.0
                else 1
            )
            return (
                self.amount_class(self["balance"], blockchain_instance=self.blockchain)
                * ratio
            )
        else:
            raise NotImplementedError("This policy isn't implemented yet")

    def claim(self, amount=None):
        assert callable(self.blockchain.vesting_balance_withdraw)
        return self.blockchain.vesting_balance_withdraw(
            self["id"], amount=amount, account=self["owner"]
        )
