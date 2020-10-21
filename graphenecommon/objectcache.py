# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from abc import ABC, abstractmethod, abstractproperty


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


class ObjectCacheInMemory(ObjectCacheInterface, dict):
    """ This class implements an object/dict cache that comes with an
        expiration. Expired items are removed from the cache.
    """

    def __init__(self, initial_data={}, default_expiration=60, no_overwrite=False):
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
        """ Returns an element from the cache if available, else returns
            the value provided as default or None
        """
        if key in self:
            value = dict.__getitem__(self, key)
            return value["data"]

    def get(self, key, default_value=None):
        if key in self:
            return self[key]
        else:
            return default_value

    def __contains__(self, key):
        if dict.__contains__(self, key):
            value = dict.__getitem__(self, key)
            if datetime.utcnow() < value["expires"]:
                return True
            else:
                # Remove from cache
                dict.pop(self, key, None)
        return False

    def set_expiration(self, expiration):
        """ Set new default expiration time in seconds (default: 10s)
        """
        self.default_expiration = expiration

    def get_expiration(self):
        """ Return the default expiration
        """
        return self.default_expiration
