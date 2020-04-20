# -*- coding: utf-8 -*-
from ..exceptions import AssetDoesNotExistsException
from ..asset import Asset as SyncAsset
from .blockchainobject import BlockchainObject


class Asset(BlockchainObject, SyncAsset):
    """ Deals with Assets of the network.

        :param str Asset: Symbol name or object id of an asset
        :param bool full: Also obtain bitasset-data and dynamic asset data
        :param instance blockchain_instance: instance to use when accesing a RPC
        :returns: All data of an asset
        :rtype: dict

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``await Asset.refresh()``.
    """

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

    async def ensure_full(self):
        if not self.is_fully_loaded:
            self.full = True
            await self.refresh()

    async def update_cer(self, cer, account=None, **kwargs):
        """ Update the Core Exchange Rate (CER) of an asset
        """
        assert callable(self.blockchain.update_cer)
        return await self.blockchain.update_cer(
            self["symbol"], cer, account=account, **kwargs
        )
