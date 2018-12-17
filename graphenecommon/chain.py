# -*- coding: utf-8 -*-
import logging
from graphenestorage import SqliteConfigurationStore
from .instance import SharedInstance

log = logging.getLogger(__name__)


class AbstractGrapheneChain:
    def define_classes(self):
        raise NotImplementedError

    def __init__(self, node="", rpcuser="", rpcpassword="", debug=False, **kwargs):

        self.define_classes()
        assert self.rpc_class
        assert self.wallet_class
        assert self.default_key_store_app_name
        assert self.transactionbuilder_class
        assert self.proposalbuilder_class
        assert self.account_class
        assert self.blockchainobject_class

        # More specific set of APIs to register to
        if "apis" not in kwargs:
            kwargs["apis"] = ["database", "network_broadcast"]

        self.rpc = None
        self.debug = debug

        self.offline = bool(kwargs.get("offline", False))
        self.nobroadcast = bool(kwargs.get("nobroadcast", False))
        self.unsigned = bool(kwargs.get("unsigned", False))
        self.expiration = int(kwargs.get("expiration", 30))
        self.bundle = bool(kwargs.get("bundle", False))
        self.blocking = bool(kwargs.get("blocking", False))

        # Legacy Proposal attributes
        self.proposer = kwargs.get("proposer", None)
        self.proposal_expiration = int(kwargs.get("proposal_expiration", 60 * 60 * 24))
        self.proposal_review = int(kwargs.get("proposal_review", 0))

        # Store self.config for access through other Classes
        kwargs["appname"] = self.default_key_store_app_name
        self.config = kwargs.get("config_store", SqliteConfigurationStore(**kwargs))

        # Connect
        if not self.offline:
            self.connect(node=node, rpcuser=rpcuser, rpcpassword=rpcpassword, **kwargs)

        # txbuffers/propbuffer are initialized and cleared
        self.clear()

        self.wallet = kwargs.get(
            "wallet", self.wallet_class(blockchain_instance=self, **kwargs)
        )

    # -------------------------------------------------------------------------
    # RPC
    # -------------------------------------------------------------------------
    def connect(self, node="", rpcuser="", rpcpassword="", **kwargs):
        """ Connect to BitShares network (internal use only)
        """
        if not node:
            if "node" in self.config:
                node = self.config["node"]
            else:
                raise ValueError("A BitShares node needs to be provided!")

        if not rpcuser and "rpcuser" in self.config:
            rpcuser = self.config["rpcuser"]

        if not rpcpassword and "rpcpassword" in self.config:
            rpcpassword = self.config["rpcpassword"]

        self.rpc = self.rpc_class(node, rpcuser, rpcpassword, **kwargs)

    def is_connected(self):
        return bool(self.rpc)

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------
    @property
    def prefix(self):
        """ Contains the prefix of the blockchain
        """
        return self.rpc.chain_params["prefix"]

    def set_blocking(self, block=True):
        """ This sets a flag that forces the broadcast to block until the
            transactions made it into a block
        """
        self.blocking = block

    def info(self):
        """ Returns the global properties
        """
        return self.rpc.get_dynamic_global_properties()

    # -------------------------------------------------------------------------
    # Wallet
    # -------------------------------------------------------------------------
    def set_default_account(self, account):
        """ Set the default account to be used
        """
        self.account_class(account)
        self.config["default_account"] = account

    def newWallet(self, pwd):
        return self.new_wallet(pwd)

    def new_wallet(self, pwd):
        """ Create a new wallet. This method is basically only calls
            :func:`bitshares.wallet.create`.

            :param str pwd: Password to use for the new wallet
            :raises bitshares.exceptions.WalletExists: if there is already a
                wallet created
        """
        return self.wallet.create(pwd)

    def unlock(self, *args, **kwargs):
        """ Unlock the internal wallet
        """
        return self.wallet.unlock(*args, **kwargs)

    # -------------------------------------------------------------------------
    # Shared instance interface
    # -------------------------------------------------------------------------
    def set_shared_instance(self):
        """ This method allows to set the current instance as default
        """
        SharedInstance.instance = self

    def finalizeOp(self, ops, account, permission, **kwargs):
        """ This method obtains the required private keys if present in
            the wallet, finalizes the transaction, signs it and
            broadacasts it

            :param operation ops: The operation (or list of operaions) to
                broadcast
            :param operation account: The account that authorizes the
                operation
            :param string permission: The required permission for
                signing (active, owner, posting)
            :param object append_to: This allows to provide an instance of
                ProposalsBuilder (see :func:`bitshares.new_proposal`) or
                TransactionBuilder (see :func:`bitshares.new_tx()`) to specify
                where to put a specific operation.

            ... note:: ``append_to`` is exposed to every method used in the
                BitShares class

            ... note::

                If ``ops`` is a list of operation, they all need to be
                signable by the same key! Thus, you cannot combine ops
                that require active permission with ops that require
                posting permission. Neither can you use different
                accounts for different operations!

            ... note:: This uses ``bitshares.txbuffer`` as instance of
                :class:`bitshares.transactionbuilder.TransactionBuilder`.
                You may want to use your own txbuffer
        """
        if "append_to" in kwargs and kwargs["append_to"]:
            if self.proposer:
                log.warn(
                    "You may not use append_to and bitshares.proposer at "
                    "the same time. Append bitshares.new_proposal(..) instead"
                )
            # Append to the append_to and return
            append_to = kwargs["append_to"]
            parent = append_to.get_parent()
            assert isinstance(
                append_to, (self.transactionbuilder_class, self.proposalbuilder_class)
            )
            append_to.appendOps(ops)
            # Add the signer to the buffer so we sign the tx properly
            if isinstance(append_to, self.proposalbuilder_class):
                parent.appendSigner(append_to.proposer, permission)
            else:
                parent.appendSigner(account, permission)
            # This returns as we used append_to, it does NOT broadcast, or sign
            return append_to.get_parent()
        elif self.proposer:
            # Legacy proposer mode!
            proposal = self.proposal()
            proposal.set_proposer(self.proposer)
            proposal.set_expiration(self.proposal_expiration)
            proposal.set_review(self.proposal_review)
            proposal.appendOps(ops)
            # Go forward to see what the other options do ...
        else:
            # Append tot he default buffer
            self.txbuffer.appendOps(ops)

        # The API that obtains the fee only allows to specify one particular
        # fee asset for all operations in that transaction even though the
        # blockchain itself could allow to pay multiple operations with
        # different fee assets.
        if "fee_asset" in kwargs and kwargs["fee_asset"]:
            self.txbuffer.set_fee_asset(kwargs["fee_asset"])

        # Add signing information, signer, sign and optionally broadcast
        if self.unsigned:
            # In case we don't want to sign anything
            self.txbuffer.addSigningInformation(account, permission)
            return self.txbuffer
        elif self.bundle:
            # In case we want to add more ops to the tx (bundle)
            self.txbuffer.appendSigner(account, permission)
            return self.txbuffer.json()
        else:
            # default behavior: sign + broadcast
            self.txbuffer.appendSigner(account, permission)
            self.txbuffer.sign()
            return self.txbuffer.broadcast()

    def sign(self, tx=None, wifs=[]):
        """ Sign a provided transaction witht he provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        if tx:
            txbuffer = self.transactionbuilder_class(tx, blockchain_instance=self)
        else:
            txbuffer = self.txbuffer
        txbuffer.appendWif(wifs)
        txbuffer.appendMissingSignatures()
        txbuffer.sign()
        return txbuffer.json()

    def broadcast(self, tx=None):
        """ Broadcast a transaction to the BitShares network

            :param tx tx: Signed transaction to broadcast
        """
        if tx:
            # If tx is provided, we broadcast the tx
            return self.transactionbuilder_class(
                tx, blockchain_instance=self
            ).broadcast()
        else:
            return self.txbuffer.broadcast()

    # -------------------------------------------------------------------------
    # Transaction Buffers
    # -------------------------------------------------------------------------
    @property
    def txbuffer(self):
        """ Returns the currently active tx buffer
        """
        return self.tx()

    @property
    def propbuffer(self):
        """ Return the default proposal buffer
        """
        return self.proposal()

    def tx(self):
        """ Returns the default transaction buffer
        """
        return self._txbuffers[0]

    def proposal(self, proposer=None, proposal_expiration=None, proposal_review=None):
        """ Return the default proposal buffer

            ... note:: If any parameter is set, the default proposal
               parameters will be changed!
        """
        if not self._propbuffer:
            return self.new_proposal(
                self.tx(), proposer, proposal_expiration, proposal_review
            )
        if proposer:
            self._propbuffer[0].set_proposer(proposer)
        if proposal_expiration:
            self._propbuffer[0].set_expiration(proposal_expiration)
        if proposal_review:
            self._propbuffer[0].set_review(proposal_review)
        return self._propbuffer[0]

    def new_proposal(
        self,
        parent=None,
        proposer=None,
        proposal_expiration=None,
        proposal_review=None,
        **kwargs
    ):
        if not parent:
            parent = self.tx()
        if not proposal_expiration:
            proposal_expiration = self.proposal_expiration

        if not proposal_review:
            proposal_review = self.proposal_review

        if not proposer:
            if "default_account" in self.config:
                proposer = self.config["default_account"]

        # Else, we create a new object
        proposal = self.proposalbuilder_class(
            proposer,
            proposal_expiration,
            proposal_review,
            blockchain_instance=self,
            parent=parent,
            **kwargs
        )
        if parent:
            parent.appendOps(proposal)
        self._propbuffer.append(proposal)
        return proposal

    def new_tx(self, *args, **kwargs):
        """ Let's obtain a new txbuffer

            :returns int txid: id of the new txbuffer
        """
        builder = self.transactionbuilder_class(
            *args, blockchain_instance=self, **kwargs
        )
        self._txbuffers.append(builder)
        return builder

    # -------------------------------------------------------------------------
    # Caches
    # -------------------------------------------------------------------------
    def clear(self):
        self._txbuffers = []
        self._propbuffer = []
        # Base/Default proposal/tx buffers
        self.new_tx()
        # self.new_proposal()

    def clear_cache(self):
        """ Clear Caches
        """
        self.blockchainobject_class.clear_cache()
