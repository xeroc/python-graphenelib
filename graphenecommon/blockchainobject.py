# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, timedelta
from .instance import AbstractBlockchainInstanceProvider
from .objectcache import ObjectCacheInMemory

ObjectCache = ObjectCacheInMemory


class Caching:
    """This class implements a few common methods that are used to
    either cache lists or dicts
    """

    __caching_args = set()
    __caching_kwargs = dict()
    __caching_klass = ObjectCacheInMemory
    _cache = ObjectCacheInMemory()

    @staticmethod
    def set_cache_store(klass, *args, **kwargs):
        Caching.__caching_args = args
        Caching.__caching_kwargs = kwargs
        Caching.__caching_klass = klass
        Caching._cache = klass(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self._fetched = False

    def _store_item(self, key=None):
        if key is None and dict.__contains__(self, "id"):
            self._cache[self.get("id")] = self
        elif key:
            self._cache[key] = self
        self._fetched = True

    def _store_items(self, key=None):
        key = key or self.__class__.__name__
        if key in self._cache:
            # check for duplicates. race condition when loading might cause that store_items is called twice with same list
            toadd = []
            for x in list(self):
                if x not in self._cache[key]:
                    toadd.append(x)
            self._cache[key].extend(toadd)
        else:
            self._cache[key] = list(self)
        self._fetched = True

    def incached(self, id):
        """Is an element cached?"""
        return id in self._cache

    def getfromcache(self, id):
        """Get an element from the cache explicitly"""
        return self._cache.get(id, None)

    def __getitem__(self, key):
        if not self._fetched:
            self.refresh()
        return dict.__getitem__(self, key)

    def items(self):
        """This overwrites items() so that refresh() is called if the
        object is not already fetched
        """
        if not self._fetched:
            self.refresh()
        return dict.items(self)

    def __contains__(self, key):
        if not self._fetched:
            self.refresh()
        return dict.__contains__(self, key)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.identifier))

    @classmethod
    def clear_cache(cls):
        """Clear/Reset the entire Cache"""
        cls._cache = ObjectCacheInMemory()

    __str__ = __repr__


class BlockchainObjects(Caching, list):
    """This class is used internally to store **lists** of objects and
    deal with the cache and indexing thereof.
    """

    identifier = None

    def refresh(self, *args, **kwargs):
        """Interface that needs to be implemented. This method is
        called when an object is requested that has not yet been
        fetched/stored
        """
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)
        # Some lists are specific to some key value that is then provided as
        # first argument
        if len(args) > 0 and isinstance(args[0], str):
            key = self._cache_key(args[0])
        else:
            key = self._cache_key()
        if self.incached(key) and self.getfromcache(key):
            list.__init__(self, self.getfromcache(key))
        else:
            if kwargs.get("refresh", True):
                self.refresh(*args, **kwargs)
        if args:
            self.identifier = args[0]

    def _cache_key(self, key=""):
        if key:
            # We add the key to the index
            return "{}-{}".format(self.__class__.__name__, key)
        else:
            return self.__class__.__name__

    def store(self, data, key=None, *args, **kwargs):
        """Cache the list

        :param list data: List of objects to cache
        """
        list.__init__(self, data)
        self._store_items(self._cache_key(key))

    @classmethod
    def cache_objects(cls, data, key=None):
        """This classmethod allows to feed multiple objects into the
        cache is is mostly used for testing
        """
        return cls._import(data, key)

    @classmethod
    def _import(cls, data, key=None):
        c = cls(key, refresh=False)
        c.store(data, key)
        return c

    # legacy
    def cache(self, key):
        """(legacy) store the current object with key ``key``."""
        self.store(self, key)

    def __getitem__(self, key):
        """Since we've overwriten __getitem__ in cache and inherit from there,
        we need to make sure we use `list` here instead of `dict`.
        """
        if not self._fetched:
            self.refresh()
        return list.__getitem__(self, key)


class BlockchainObject(Caching, dict):
    """This class deals with objects from graphene-based blockchains.
    It is used to validate object ids, store entire objects in
    the cache and deal with indexing thereof.
    """

    space_id = 1
    type_id = None
    perform_id_tests = True
    type_ids = []
    identifier = None

    def __init__(self, data, klass=None, lazy=False, use_cache=True, *args, **kwargs):
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
                self.refresh()
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
                self.refresh()

        if self._use_cache and not self._lazy:
            self._store_item()

    def store(self, data, key="id"):
        """Cache the list

        :param list data: List of objects to cache
        """
        dict.__init__(self, data)
        self._store_item(key)

    @classmethod
    def cache_object(cls, data, key=None):
        """This classmethod allows to feed an object into the
        cache is is mostly used for testing
        """
        return cls._import(data, key)

    @classmethod
    def _import(cls, data, key=None):
        c = cls(data, refresh=False)
        c.store(data, key)
        return c

    @staticmethod
    def objectid_valid(i):
        """Test if a string looks like a regular object id of the
        form:::

           xxxx.yyyyy.zzzz

        with those being numbers.
        """
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
        """Alias for objectid_valid"""
        return self.objectid_valid(i)

    def testid(self, id):
        """In contrast to validity, this method tests if the objectid
        matches the type_id provided in self.type_id or self.type_ids
        """
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
    """This class is a basic class that allows to obtain any object
    from the blockchyin by fetching it through the API
    """

    def refresh(self):
        """This is the refresh method that overloads the prototype in
        BlockchainObject.
        """
        dict.__init__(
            self,
            self.blockchain.rpc.get_object(self.identifier),
            blockchain_instance=self.blockchain,
        )
