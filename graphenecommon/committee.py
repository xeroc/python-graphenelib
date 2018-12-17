# -*- coding: utf-8 -*-
from .blockchainobject import BlockchainObject
from .exceptions import CommitteeMemberDoesNotExistsException
from .instance import AbstractBlockchainInstanceProvider


class Committee(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ Read data about a Committee Member in the chain

        :param str member: Name of the Committee Member
        :param instance blockchain_instance: instance to use when accesing a RPC
        :param bool lazy: Use lazy loading

    """

    def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id
        assert self.account_class
        BlockchainObject.__init__(self, *args, **kwargs)

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 2:
                account = self.account_class(
                    self.identifier, blockchain_instance=self.blockchain
                )
                member = self.blockchain.rpc.get_committee_member_by_account(
                    account["id"]
                )
            elif int(i) == 5:
                member = self.blockchain.rpc.get_object(self.identifier)
            else:
                raise CommitteeMemberDoesNotExistsException
        else:
            # maybe identifier is an account name
            account = self.account_class(
                self.identifier, blockchain_instance=self.blockchain
            )
            member = self.blockchain.rpc.get_committee_member_by_account(account["id"])

        if not member:
            raise CommitteeMemberDoesNotExistsException
        super(Committee, self).__init__(member, blockchain_instance=self.blockchain)

    @property
    def account_id(self):
        return self.get("committee_member_account")

    @property
    def account(self):
        return self.account_class(self.account_id, blockchain_instance=self.blockchain)
