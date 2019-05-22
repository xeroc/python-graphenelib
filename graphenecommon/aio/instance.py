# -*- coding: utf-8 -*-
from ..instance import (
    AbstractBlockchainInstanceProvider as SyncAbstractBlockchainInstanceProvider,
)


class AbstractBlockchainInstanceProvider(SyncAbstractBlockchainInstanceProvider):
    @classmethod
    def inject(slf, cls):
        class NewClass(slf, cls):
            blockchain_instance_class = slf

            async def __init__(self, *args, **kwargs):
                slf.__init__(self, *args, **kwargs)
                await cls.__init__(self, *args, **kwargs)

        NewClass.__name__ = cls.__name__
        NewClass.__qualname__ = cls.__qualname__
        NewClass.__doc__ = cls.__doc__
        NewClass.__module__ = cls.__module__
        return NewClass
