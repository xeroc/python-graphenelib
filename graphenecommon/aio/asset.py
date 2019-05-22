# -*- coding: utf-8 -*-
from ..exceptions import AssetDoesNotExistsException
from ..asset import Asset as SyncAsset
from .blockchainobject import BlockchainObject


class Asset(BlockchainObject, SyncAsset):
    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id

        self.full = kwargs.pop("full", False)
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        """ Refresh the data from the API server
        """
        asset = await self.blockchain.rpc.get_asset(self.identifier)
        if not asset:
            raise AssetDoesNotExistsException(self.identifier)
        await super(Asset, self).__init__(asset, blockchain_instance=self.blockchain)
        if self.full:
            if "bitasset_data_id" in asset:
                self["bitasset_data"] = await self.blockchain.rpc.get_object(
                    asset["bitasset_data_id"]
                )
            self["dynamic_asset_data"] = await self.blockchain.rpc.get_object(
                asset["dynamic_asset_data_id"]
            )

    async def update_cer(self, cer, account=None, **kwargs):
        """ Update the Core Exchange Rate (CER) of an asset
        """
        assert callable(self.blockchain.update_cer)
        return await self.blockchain.update_cer(
            self["symbol"], cer, account=account, **kwargs
        )
