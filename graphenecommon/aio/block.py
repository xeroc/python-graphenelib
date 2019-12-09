# -*- coding: utf-8 -*-
from .blockchainobject import BlockchainObject
from ..block import Block as SyncBlock, BlockHeader as SyncBlockHeader
from ..exceptions import BlockDoesNotExistsException


class Block(BlockchainObject, SyncBlock):
    """ Read a single block from the chain

        :param int block: block number
        :param instance blockchain_instance: instance to use when accesing a RPC
        :param bool lazy: Use lazy loading
        :param loop: asyncio event loop

        Instances of this class are dictionaries that come with additional
        methods (see below) that allow dealing with a block and it's
        corresponding functions.

        .. code-block:: python

            from aio.block import Block
            block = await Block(1)
            print(block)
    """

    async def __init__(self, *args, use_cache=False, **kwargs):
        # We allow to hand over use_cache be default, but here,
        # we want to change the default to *false* so we don't cache every
        # block all the time for eternity
        kwargs["use_cache"] = use_cache
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        """ Even though blocks never change, you freshly obtain its contents
            from an API with this method
        """
        block = await self.blockchain.rpc.get_block(self.identifier)
        if not block:
            raise BlockDoesNotExistsException
        await super(Block, self).__init__(
            block, blockchain_instance=self.blockchain, use_cache=self._use_cache
        )


class BlockHeader(BlockchainObject, SyncBlockHeader):
    async def __init__(self, *args, use_cache=False, **kwargs):
        # We allow to hand over use_cache be default, but here,
        # we want to change the default to *false* so we don't cache every
        # block all the time for eternity
        kwargs["use_cache"] = use_cache
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        """ Even though blocks never change, you freshly obtain its contents
            from an API with this method
        """
        block = await self.blockchain.rpc.get_block_header(self.identifier)
        if not block:
            raise BlockDoesNotExistsException
        await super(BlockHeader, self).__init__(
            block, blockchain_instance=self.blockchain, use_cache=self._use_cache
        )
