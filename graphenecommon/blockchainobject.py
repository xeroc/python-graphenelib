# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from .instance import AbstractBlockchainInstanceProvider


class ObjectCache(dict):
    def __init__(self, initial_data={}, default_expiration=10, no_overwrite=False):
        dict.__init__(self, initial_data)

        # Expiration
        self.set_expiration(default_expiration)

        # This allows nicer testing
        self.no_overwrite = no_overwrite

    def __setitem__(self, key, value):
        if key in self and not self.no_overwrite:
            del self[key]
        elif key in self and self.no_overwrite:
            return
        data = {
            "expires": datetime.utcnow() + timedelta(seconds=self.default_expiration),
            "data": value,
        }
        dict.__setitem__(self, key, data)

    def __getitem__(self, key):
        if key in self:
            value = dict.__getitem__(self, key)
            return value["data"]

    def get(self, key, default):
        if key in self:
            return self[key]
        else:
            return default

    def __contains__(self, key):
        if dict.__contains__(self, key):
            value = dict.__getitem__(self, key)
            if datetime.utcnow() < value["expires"]:
                return True
        return False

    def __str__(self):
        return "ObjectCache(n={}, default_expiration={})".format(
            len(self.keys()), self.default_expiration
        )

    def set_expiration(self, expiration):
        self.default_expiration = expiration


class Caching:
    def _store_item(self, key=None):
        if key is None and dict.__contains__(self, "id"):
            self._cache[self.get("id")] = self
        elif key:
            self._cache[key] = self
        self._cached = True

    def _store_items(self, key=None):
        key = key or self.__class__.__name__
        self._cache[key] = list(self)
        self._cached = True

    def incached(self, id):
        return id in self._cache

    def getfromcache(self, id):
        return self._cache.get(id, None)

    def __getitem__(self, key):
        if not self._cached:
            self.refresh()
        return dict.__getitem__(self, key)

    def items(self):
        if not self._cached:
            self.refresh()
        return dict.items(self)

    def __contains__(self, key):
        if not self._cached:
            self.refresh()
        return dict.__contains__(self, key)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.identifier))

    @classmethod
    def clear_cache(cls):
        cls._cache = ObjectCache()

    __str__ = __repr__


class BlockchainObjects(list, Caching):
    _cache = ObjectCache()
    identifier = None

    @property
    def _cache_key(self):
        key = self.__class__.__name__
        key += self.identifier or ""
        return key

    def __init__(self, *args, **kwargs):
        key = self._cache_key
        if self.incached(key):
            list.__init__(self, self.getfromcache(key))
        else:
            if kwargs.get("refresh", True):
                self.refresh(*args, **kwargs)

    def store(self, data, *args, **kwargs):
        list.__init__(self, data)
        self._store_items(self._cache_key)

    def refresh(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _import(cls, data, key=None):
        c = cls(key, refresh=False)
        c.store(data, key)
        return c

    # legacy
    def cache(self, key):
        self.store(self, key)


class BlockchainObject(dict, Caching):

    space_id = 1
    type_id = None
    type_ids = []
    identifier = None

    _cache = ObjectCache()

    def __init__(self, data, klass=None, lazy=False, use_cache=True, *args, **kwargs):
        assert self.type_id or self.type_ids
        self.cached = False

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
                self.cached = True
            if not lazy and not self.cached:
                self.refresh()
            # make sure to store the blocknumber for caching
            self["id"] = str(data)
            # Set identifier again as it is overwritten in super() in refresh()
            self.identifier = data
        else:
            self.identifier = data
            if self.test_valid_objectid(self.identifier):
                # Here we assume we deal with an id
                self.testid(self.identifier)
            if self.incached(data):
                dict.__init__(self, dict(self.getfromcache(data)))
            elif not lazy and not self.cached:
                self.refresh()

        if use_cache and not lazy:
            self._store_item()

    def store(self, data, key="id"):
        dict.__init__(self, data)
        self._store_item(key)

    @staticmethod
    def objectid_valid(i):
        if "." not in i:
            return False
        parts = i.split(".")
        if len(parts) == 3:
            try:
                [int(x) for x in parts]
                return True
            except Exception:
                pass
            return False

    def test_valid_objectid(self, i):
        return self.objectid_valid(i)

    def testid(self, id):
        parts = id.split(".")
        if not self.type_id:
            return

        if not self.type_ids:
            self.type_ids = [self.type_id]

        assert int(parts[0]) == self.space_id, "Valid id's for {} are {}.{}.x".format(
            self.__class__.__name__, self.space_id, self.type_id
        )
        assert int(parts[1]) in self.type_ids, "Valid id's for {} are {}.{}.x".format(
            self.__class__.__name__, self.space_id, self.type_ids
        )


class Object(BlockchainObject, AbstractBlockchainInstanceProvider):
    def refresh(self):
        dict.__init__(
            self,
            self.blockchain.rpc.get_object(self.identifier),
            blockchain_instance=self.blockchain,
        )
