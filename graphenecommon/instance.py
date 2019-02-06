# -*- coding: utf-8 -*-
from functools import update_wrapper
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
        if not SharedInstance.instance:
            klass = self.get_instance_class()
            SharedInstance.instance = klass(**SharedInstance.config)
        return SharedInstance.instance

    @staticmethod
    def set_shared_blockchain_instance(instance):
        """ This method allows us to override default instance for all
            users of ``SharedInstance.instance``.

            :param chaininstance instance: Chain instance
        """
        SharedInstance.instance = instance


# Legacy alias
BlockchainInstance = AbstractBlockchainInstanceProvider
