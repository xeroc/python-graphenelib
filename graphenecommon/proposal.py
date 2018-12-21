# -*- coding: utf-8 -*-
import logging

from .blockchainobject import BlockchainObject, BlockchainObjects
from .exceptions import ProposalDoesNotExistException
from .instance import AbstractBlockchainInstanceProvider
from .utils import parse_time


log = logging.getLogger(__name__)


class Proposal(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    def __init__(self, data, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        BlockchainObject.__init__(self, data, *args, **kwargs)

    def refresh(self):
        proposal = self.blockchain.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0], blockchain_instance=self.blockchain)

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]

    @property
    def proposer(self):
        """ Return the proposer of the proposal if available in the backend,
            else returns None
        """
        if "proposer" in self:
            return self.account_class(self["proposer"])

    @property
    def expiration(self):
        return parse_time(self.get("expiration_time"))

    @property
    def review_period(self):
        return parse_time(self.get("review_period_time"))

    @property
    def is_in_review(self):
        from datetime import datetime, timezone

        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return now > self.review_period


class Proposals(BlockchainObjects, AbstractBlockchainInstanceProvider):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param instance blockchain_instance: instance to use when accesing a RPC
    """

    def __init__(self, account, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.proposal_class

        assert isinstance(account, str)
        self.identifier = account
        BlockchainObjects.__init__(self, account, *args, **kwargs)

    def refresh(self, *args, **kwargs):
        account = self.account_class(self.identifier)
        proposals = self.blockchain.rpc.get_proposed_transactions(account["id"])
        data = [
            self.proposal_class(x, blockchain_instance=self.blockchain)
            for x in proposals
        ]
        self.store(data, account["id"])
        self.store(data, account["name"])
