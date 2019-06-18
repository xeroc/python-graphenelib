# -*- coding: utf-8 -*-
from .blockchainobject import BlockchainObject, BlockchainObjects
from ..exceptions import CommitteeMemberDoesNotExistsException
from ..committee import Committee as SyncCommittee


class Committee(BlockchainObject, SyncCommittee):
    """ Read data about a Committee Member in the chain

        :param str member: Name of the Committee Member
        :param instance blockchain_instance: instance to use when accesing a RPC
        :param bool lazy: Use lazy loading

    """

    async def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id
        assert self.account_class
        await BlockchainObject.__init__(self, *args, **kwargs)

    async def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 2:
                account = await self.account_class(
                    self.identifier, blockchain_instance=self.blockchain
                )
                member = await self.blockchain.rpc.get_committee_member_by_account(
                    account["id"]
                )
            elif int(i) == 5:
                member = await self.blockchain.rpc.get_object(self.identifier)
            else:
                raise CommitteeMemberDoesNotExistsException
        else:
            # maybe identifier is an account name
            account = await self.account_class(
                self.identifier, blockchain_instance=self.blockchain
            )
            member = await self.blockchain.rpc.get_committee_member_by_account(
                account["id"]
            )

        if not member:
            raise CommitteeMemberDoesNotExistsException
        await super(Committee, self).__init__(
            member, blockchain_instance=self.blockchain
        )

    @property
    async def account(self):
        return await self.account_class(
            self.account_id, blockchain_instance=self.blockchain
        )
