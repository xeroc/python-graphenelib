# -*- coding: utf-8 -*-
from asyncinit import asyncinit

from .instance import AbstractBlockchainInstanceProvider
from ..blockchainobject import (
    Caching as SyncCaching,
    BlockchainObjects as SyncBlockchainObjects,
    BlockchainObject as SyncBlockchainObject,
)


class Caching(SyncCaching):
    def __getitem__(self, key):
        """ This method overrides synchronous version to avoid calling
            self.refresh()
        """
        return dict.__getitem__(self, key)

    async def items(self):
        """ This overrides items() so that refresh() is called if the
            object is not already fetched
        """
        if not self._fetched:
            await self.refresh()
        return dict.items(self)

    def __contains__(self, key):
        """ This method overrides synchronous version to avoid calling
            self.refresh()
        """
        return dict.__contains__(self, key)


@asyncinit
class BlockchainObjects(Caching, list):
    async def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)
        # Some lists are specific to some key value that is then provided as
        # first argument
        if len(args) > 0 and isinstance(args[0], str):
            key = self._cache_key(args[0])
        else:
            key = self._cache_key()
        if self.incached(key):
            list.__init__(self, self.getfromcache(key))
        else:
            if kwargs.get("refresh", True):
                await self.refresh(*args, **kwargs)

    def __getitem__(self, key):
        """ Since we've overwriten __getitem__ in cache and inherit from there,
            we need to make sure we use `list` here instead of `dict`.

            This method overrides synchronous version to avoid calling
            self.refresh()
        """
        return list.__getitem__(self, key)


@asyncinit
class BlockchainObject(Caching, SyncBlockchainObject):
    async def __init__(
        self, data, klass=None, lazy=False, use_cache=True, *args, **kwargs
    ):
        Caching.__init__(self, *args, **kwargs)
        self._use_cache = use_cache
        if self.perform_id_tests:
            assert self.type_id or self.type_ids, "Need type_id or type_ids"
        self._fetched = False
        self._lazy = lazy

        if "_cache_expiration" in kwargs:
            self.set_expiration(kwargs["_cache_expiration"])

        # We don't read lists, sets, or tuples
        if isinstance(data, (list, set, tuple)):
            raise ValueError(
                "Cannot interpret lists! Please load elements individually!"
            )

        if klass and isinstance(data, klass):
            self.identifier = data.get("id")
            dict.__init__(self, data)
        elif isinstance(data, dict):
            self.identifier = data.get("id")
            dict.__init__(self, data)
        elif isinstance(data, int):
            # This is only for block number bascially
            self.identifier = data
            if self.incached(str(data)):
                dict.__init__(self, self.getfromcache(str(data)))
                self._fetched = True
            if not self._lazy and not self._fetched:
                await self.refresh()
            # make sure to store the blocknumber for caching
            self["id"] = str(data)
            # Set identifier again as it is overwritten in super() in refresh()
            self.identifier = data
        else:
            self.identifier = data
            if self.perform_id_tests and self.test_valid_objectid(self.identifier):
                # Here we assume we deal with an id
                self.testid(self.identifier)

            if self.incached(data):
                dict.__init__(self, dict(self.getfromcache(data)))
            elif not self._lazy and not self._fetched:
                await self.refresh()

        if self._use_cache and not self._lazy:
            self._store_item()


class Object(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ This class is a basic class that allows to obtain any object
        from the blockchyin by fetching it through the API
    """

    async def refresh(self):
        """ This is the refresh method that overloads the prototype in
            BlockchainObject.
        """
        dict.__init__(
            self,
            await self.blockchain.rpc.get_object(self.identifier),
            blockchain_instance=self.blockchain,
        )
