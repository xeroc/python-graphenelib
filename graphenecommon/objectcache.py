# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from abc import ABC, abstractmethod, abstractproperty
from expiringdict import ExpiringDict


class ObjectCacheInterface:
    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def get(self, key, default_value=None):
        pass

    @abstractmethod
    def __contains__(self, key):
        pass

    @abstractmethod
    def set_expiration(self, value):
        pass

    @abstractmethod
    def get_expiration(self):
        pass

    def __str__(self):
        return "{}(default_expiration={})".format(
            self.__class__.__name__, self.get_expiration()
        )


class ObjectCacheInMemory(ExpiringDict, ObjectCacheInterface):
    """ This class implements an object/dict cache that comes with an
        expiration. Expired items are removed from the cache. The cache has a
        max_length.
    """

    def __init__(
        self,
        initial_data={},
        default_expiration=60,
        no_overwrite=False,
        max_length=1000,
    ):
        dict.__init__(self, initial_data)

        # Expiration
        self.default_expiration = default_expiration

        # This allows nicer testing
        self.no_overwrite = no_overwrite

        # Number of items to store (in total)
        self._max_items = max_length

        ExpiringDict.__init__(
            self, max_len=self._max_items, max_age_seconds=self.default_expiration
        )

    def set_expiration(self, expiration):
        """ Set new default expiration time in seconds (default: 10s)
        """
        self.default_expiration = expiration

    def get_expiration(self):
        """ Return the default expiration
        """
        return self.default_expiration
