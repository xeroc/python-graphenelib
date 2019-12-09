# -*- coding: utf-8 -*-
from asyncinit import asyncinit

from .asset import Asset
from ..amount import Amount as SyncAmount


@asyncinit
class Amount(SyncAmount):
    async def __init__(self, *args, **kwargs):
        """ Async version of :class:`..amount.Amount`

            Limitations: most of arithmetic operations are not supported on async version
        """
        self.define_classes()
        assert self.asset_class

        self["asset"] = {}

        amount = kwargs.get("amount", None)
        asset = kwargs.get("asset", None)

        if len(args) == 1 and isinstance(args[0], Amount):
            # Copy Asset object
            self["amount"] = args[0]["amount"]
            self["symbol"] = args[0]["symbol"]
            self["asset"] = args[0]["asset"]

        elif len(args) == 1 and isinstance(args[0], str):
            self["amount"], self["symbol"] = args[0].split(" ")
            self["asset"] = await self.asset_class(
                self["symbol"], blockchain_instance=self.blockchain
            )

        elif (
            len(args) == 1
            and isinstance(args[0], dict)
            and "amount" in args[0]
            and "asset_id" in args[0]
        ):
            self["asset"] = await self.asset_class(
                args[0]["asset_id"], blockchain_instance=self.blockchain
            )
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = int(args[0]["amount"]) / 10 ** self["asset"]["precision"]

        elif (
            len(args) == 1
            and isinstance(args[0], dict)
            and "amount" in args[0]
            and "asset" in args[0]
        ):
            self["asset"] = await self.asset_class(
                args[0]["asset"], blockchain_instance=self.blockchain
            )
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = int(args[0]["amount"]) / 10 ** self["asset"]["precision"]

        elif len(args) == 2 and isinstance(args[1], Asset):
            self["amount"] = args[0]
            self["symbol"] = args[1]["symbol"]
            self["asset"] = args[1]

        elif len(args) == 2 and isinstance(args[1], str):
            self["amount"] = args[0]
            self["asset"] = await self.asset_class(
                args[1], blockchain_instance=self.blockchain
            )
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (int, float)) and asset and isinstance(asset, Asset):
            self["amount"] = amount
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (int, float)) and asset and isinstance(asset, dict):
            self["amount"] = amount
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        elif isinstance(amount, (int, float)) and asset and isinstance(asset, str):
            self["amount"] = amount
            self["asset"] = await self.asset_class(
                asset, blockchain_instance=self.blockchain
            )
            self["symbol"] = asset

        else:
            raise ValueError

        # make sure amount is a float
        self["amount"] = float(self.get("amount", 0.0))

    async def copy(self):
        """ Copy the instance and make sure not to use a reference
        """
        return await self.__class__(
            amount=self["amount"],
            asset=self["asset"].copy(),
            blockchain_instance=self.blockchain,
        )

    @property
    async def asset(self):
        """ Returns the asset as instance of :class:`.asset.Asset`
        """
        if not self["asset"]:
            self["asset"] = await self.asset_class(
                self["symbol"], blockchain_instance=self.blockchain
            )
        return self["asset"]

    def __floordiv__(self, other):
        raise NotImplementedError("Async version does not support __floordiv__")

    def __div__(self, other):
        raise NotImplementedError("Async version does not support __div__")

    def __sub__(self, other):
        raise NotImplementedError("Async version does not support __sub__")

    def __mod__(self, other):
        raise NotImplementedError("Async version does not support __mod__")

    def __mul__(self, other):
        raise NotImplementedError("Async version does not support __mul__")

    def __neg__(self):
        raise NotImplementedError("Async version does not support __neg__")

    def __add__(self, other):
        raise NotImplementedError("Async version does not support __add__")

    def __pow__(self, other):
        raise NotImplementedError("Async version does not support __pow__")
