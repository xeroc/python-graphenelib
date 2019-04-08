# -*- coding: utf-8 -*-
import types


class SharedInstance:
    """ This class merely offers a singelton for the Blockchain Instance
    """

    instance = None
    config = {}


class AbstractBlockchainInstanceProvider:
    """ This is a class that allows compatibility with previous
        naming conventions. It will extract 'blockchain_instance'
        from the key word arguments and ensure that self.blockchain
        contains an instance of the main chain instance
    """

    _sharedInstance = SharedInstance

    def __init__(self, *args, **kwargs):
        self._blockchain = None
        if kwargs.get("blockchain_instance"):
            self._blockchain = kwargs["blockchain_instance"]
        else:
            self._blockchain = self.shared_blockchain_instance()

    @classmethod
    def inject(slf, cls):
        class NewClass(slf, cls):
            blockchain_instance_class = slf

            def __init__(self, *args, **kwargs):
                slf.__init__(self, *args, **kwargs)
                cls.__init__(self, *args, **kwargs)

        NewClass.__name__ = cls.__name__
        NewClass.__qualname__ = cls.__qualname__
        NewClass.__doc__ = cls.__doc__
        NewClass.__module__ = cls.__module__
        return NewClass

    def get_instance_class(self):
        """ Should return the Chain instance class, e.g. `bitshares.BitShares`
        """
        raise NotImplementedError

    def define_classes(self):
        """ Needs to define instance variables that provide classes
        """
        raise NotImplementedError

    @property
    def blockchain(self):
        if hasattr(self, "_blockchain") and self._blockchain:
            # This shouldn't happen except for legacy libraries
            return self._blockchain
        else:
            return self.shared_blockchain_instance()

    @property
    def chain(self):
        """ Short form for blockchain (for the lazy)
        """
        return self.blockchain

    def shared_blockchain_instance(self):
        """ This method will initialize ``SharedInstance.instance`` and return it.
            The purpose of this method is to have offer single default
            instance that can be reused by multiple classes.
        """
        if not self._sharedInstance.instance:
            klass = self.get_instance_class()
            self._sharedInstance.instance = klass(**self._sharedInstance.config)
        return self._sharedInstance.instance

    @classmethod
    def set_shared_blockchain_instance(cls, instance):
        """ This method allows us to override default instance for all
            users of ``SharedInstance.instance``.

            :param chaininstance instance: Chain instance
        """
        cls._sharedInstance.instance = instance

    # -------------------------------------------------------------------------
    # Shared instance interface
    # -------------------------------------------------------------------------
    def set_shared_instance(self):
        """ This method allows to set the current instance as default
        """
        self._sharedInstance.instance = self

    @classmethod
    def set_shared_config(cls, config):
        """ This allows to set a config that will be used when calling
            ``shared_blockchain_instance`` and allows to define the configuration
            without requiring to actually create an instance
        """
        assert isinstance(config, dict)
        cls._sharedInstance.config.update(config)
        # if one is already set, delete
        if cls._sharedInstance.instance:
            cls._sharedInstance.instance = None


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    instance.clear_cache()
    BlockchainInstance.set_shared_blockchain_instance(instance)


def set_shared_config(config):
    BlockchainInstance.set_shared_config(config)


# Legacy alias
BlockchainInstance = AbstractBlockchainInstanceProvider
