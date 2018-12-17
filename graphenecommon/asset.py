# -*- coding: utf-8 -*-
import json
from .blockchainobject import BlockchainObject
from .exceptions import AssetDoesNotExistsException
from .instance import AbstractBlockchainInstanceProvider


class Asset(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ Deals with Assets of the network.

        :param str Asset: Symbol name or object id of an asset
        :param bool lazy: Lazy loading
        :param bool full: Also obtain bitasset-data and dynamic asset data
        :param instance blockchain_instance: instance to use when accesing a RPC
        :returns: All data of an asset
        :rtype: dict

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Asset.refresh()``.
    """

    def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id

        self.full = kwargs.pop("full", False)
        BlockchainObject.__init__(self, *args, **kwargs)

    def refresh(self):
        """ Refresh the data from the API server
        """
        asset = self.blockchain.rpc.get_asset(self.identifier)
        if not asset:
            raise AssetDoesNotExistsException(self.identifier)
        super(Asset, self).__init__(asset, blockchain_instance=self.blockchain)
        if self.full:
            if "bitasset_data_id" in asset:
                self["bitasset_data"] = self.blockchain.rpc.get_object(
                    asset["bitasset_data_id"]
                )
            self["dynamic_asset_data"] = self.blockchain.rpc.get_object(
                asset["dynamic_asset_data_id"]
            )

    @property
    def is_fully_loaded(self):
        """ Is this instance fully loaded / e.g. all data available?
        """
        return self.full and "bitasset_data_id" in self and "bitasset_data" in self

    @property
    def symbol(self):
        return self["symbol"]

    @property
    def precision(self):
        return self["precision"]

    @property
    def is_bitasset(self):
        """ Is the asset a :doc:`mpa`?
        """
        return "bitasset_data_id" in self

    @property
    def permissions(self):
        """ List the permissions for this asset that the issuer can obtain
        """
        return self["permissions"]

    @property
    def flags(self):
        """ List the permissions that are currently used (flags)
        """
        return self["flags"]

    def ensure_full(self):
        if not self.is_fully_loaded:
            self.full = True
            self.refresh()

    def update_cer(self, cer, account=None, **kwargs):
        """ Update the Core Exchange Rate (CER) of an asset
        """
        assert callable(self.blockchain.update_cer)
        return self.blockchain.update_cer(
            self["symbol"], cer, account=account, **kwargs
        )
