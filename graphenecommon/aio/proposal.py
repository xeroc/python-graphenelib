# -*- coding: utf-8 -*-
import logging

from .blockchainobject import BlockchainObject, BlockchainObjects
from ..exceptions import ProposalDoesNotExistException
from ..proposal import Proposal as SyncProposal, Proposals as SyncProposals


log = logging.getLogger(__name__)


class Proposal(BlockchainObject, SyncProposal):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param instance blockchain_instance: instance to use when accesing a RPC

    """

    async def __init__(self, data, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        await BlockchainObject.__init__(self, data, *args, **kwargs)

    async def refresh(self):
        proposal = await self.blockchain.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        await super(Proposal, self).__init__(
            proposal[0], blockchain_instance=self.blockchain
        )

    @property
    async def proposer(self):
        """ Return the proposer of the proposal if available in the backend,
            else returns None
        """
        if "proposer" in self:
            return await self.account_class(
                self["proposer"], blockchain_instance=self.blockchain
            )


class Proposals(BlockchainObjects, SyncProposals):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param instance blockchain_instance: instance to use when accesing a RPC
    """

    async def __init__(self, account, *args, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.proposal_class

        assert isinstance(account, str)
        self.identifier = account
        await BlockchainObjects.__init__(self, account, *args, **kwargs)

    async def refresh(self, *args, **kwargs):
        account = await self.account_class(self.identifier)
        proposals = await self.blockchain.rpc.get_proposed_transactions(account["id"])
        data = [
            await self.proposal_class(x, blockchain_instance=self.blockchain)
            for x in proposals
        ]
        self.store(data, account["id"])
        self.store(data, account["name"])
