# -*- coding: utf-8 -*-
import struct
import logging
from binascii import unhexlify
from ..exceptions import (
    InsufficientAuthorityError,
    InvalidWifError,
    MissingKeyError,
    WalletLocked,
)
from ..utils import formatTimeFromNow
from graphenebase.objects import Asset
from ..transactionbuilder import (
    ProposalBuilder as SyncProposalBuilder,
    TransactionBuilder as SyncTransactionBuilder,
)

log = logging.getLogger(__name__)


class ProposalBuilder(SyncProposalBuilder):
    """ Proposal Builder allows us to construct an independent Proposal
        that may later be added to an instance ot TransactionBuilder

        :param str proposer: Account name of the proposing user
        :param int proposal_expiration: Number seconds until the proposal is
            supposed to expire
        :param int proposal_review: Number of seconds for review of the
            proposal
        :param .transactionbuilder.TransactionBuilder: Specify
            your own instance of transaction builder (optional)
        :param instance blockchain_instance: Blockchain instance
    """

    async def broadcast(self):
        assert self.parent, "No parent transaction provided!"
        self.parent._set_require_reconstruction()
        await self.parent.sign()
        return await self.parent.broadcast()

    async def json(self):
        """ Return the json formated version of this proposal
        """
        raw = await self.get_raw()
        if not raw:
            return dict()
        return raw.json()

    def __dict__(self):
        raise NotImplementedError("Use .json() instead")

    async def get_raw(self):
        """ Returns an instance of base "Operations" for further processing
        """
        if not self.ops:
            return
        ops = [self.operations.Op_wrapper(op=o) for o in list(self.ops)]
        proposer = await self.account_class(
            self.proposer, blockchain_instance=self.blockchain
        )
        data = {
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "fee_paying_account": proposer["id"],
            "expiration_time": formatTimeFromNow(self.proposal_expiration),
            "proposed_ops": [o.json() for o in ops],
            "extensions": [],
        }
        if self.proposal_review:
            data.update({"review_period_seconds": self.proposal_review})
        ops = self.operations.Proposal_create(**data)
        return self.operation_class(ops)


class TransactionBuilder(SyncTransactionBuilder):
    """ This class simplifies the creation of transactions by adding
        operations and signers.
    """

    async def list_operations(self):
        ret = list()
        for o in self.ops:
            if isinstance(o, ProposalBuilder):
                prop = await o.get_raw()
                if prop:
                    ret.append(prop)
            else:
                ret.append(self.operation_class(o))
        return ret

    def __str__(self):
        raise NotImplementedError("Use .json() instead")

    async def json(self):
        """ Show the transaction as plain json
        """
        if not self._is_constructed() or self._is_require_reconstruction():
            await self.constructTx()
        return dict(self)

    # Let's define a helper function for recursion
    async def _fetchkeys(self, account, perm, level=0, required_treshold=1):

        # Do not travel recursion more than 2 levels
        if level > 2:
            return []

        r = []
        # Let's go through all *keys* of the account
        for authority in account[perm]["key_auths"]:
            try:
                # Try obtain the private key from wallet
                wif = self.blockchain.wallet.getPrivateKeyForPublicKey(authority[0])
            except Exception:
                continue

            if wif:
                r.append([wif, authority[1]])
                # If we found a key for account, we add it
                # to signing_accounts to be sure we do not resign
                # another operation with the same account/wif
                self.signing_accounts.append(account)

            # Test if we reached threshold already
            if sum([x[1] for x in r]) >= required_treshold:
                break

        # Let's see if we still need to go through accounts
        if sum([x[1] for x in r]) < required_treshold:
            # go one level deeper
            for authority in account[perm]["account_auths"]:
                # Let's see if we can find keys for an account in
                # account_auths
                # This is recursive with a limit at level 2 (see above)
                auth_account = await self.account_class(
                    authority[0], blockchain_instance=self.blockchain
                )
                required_treshold = auth_account[perm]["weight_threshold"]
                keys = await self._fetchkeys(
                    auth_account, perm, level + 1, required_treshold
                )

                for key in keys:
                    r.append(key)

                    # Test if we reached threshold already and break
                    if sum([x[1] for x in r]) >= required_treshold:
                        break

        return r

    async def appendSigner(self, accounts, permission):
        """ Try to obtain the wif key from the wallet by telling which account
            and permission is supposed to sign the transaction
        """
        assert permission in self.permission_types, "Invalid permission"

        if self.blockchain.wallet.locked():
            raise WalletLocked()
        if not isinstance(accounts, (list, tuple, set)):
            accounts = [accounts]

        for account in accounts:
            # Now let's actually deal with the accounts
            if account not in self.signing_accounts:
                # is the account an instance of public key?
                if isinstance(account, self.publickey_class):
                    self.appendWif(
                        self.blockchain.wallet.getPrivateKeyForPublicKey(str(account))
                    )
                # ... or should we rather obtain the keys from an account name
                else:
                    accountObj = await self.account_class(
                        account, blockchain_instance=self.blockchain
                    )
                    required_treshold = accountObj[permission]["weight_threshold"]
                    keys = await self._fetchkeys(
                        accountObj, permission, required_treshold=required_treshold
                    )
                    # If we couldn't find an active key, let's try overwrite it
                    # with an owner key
                    if not keys and permission != "owner":
                        keys.extend(
                            await self._fetchkeys(
                                accountObj, "owner", required_treshold=required_treshold
                            )
                        )
                    for x in keys:
                        self.appendWif(x[0])

                self.signing_accounts.append(account)

    async def add_required_fees(self, ops, asset_id="1.3.0"):
        """ Auxiliary method to obtain the required fees for a set of
            operations. Requires a websocket connection to a witness node!
        """
        ws = self.blockchain.rpc
        fees = await ws.get_required_fees([i.json() for i in ops], asset_id)
        for i, d in enumerate(ops):
            if isinstance(fees[i], list):
                # Operation is a proposal
                ops[i].op.data["fee"] = Asset(
                    amount=fees[i][0]["amount"], asset_id=fees[i][0]["asset_id"]
                )
                for j, _ in enumerate(ops[i].op.data["proposed_ops"].data):
                    ops[i].op.data["proposed_ops"].data[j].data["op"].op.data[
                        "fee"
                    ] = Asset(
                        amount=fees[i][1][j]["amount"],
                        asset_id=fees[i][1][j]["asset_id"],
                    )
            else:
                # Operation is a regular operation
                ops[i].op.data["fee"] = Asset(
                    amount=fees[i]["amount"], asset_id=fees[i]["asset_id"]
                )
        return ops

    async def constructTx(self):
        """ Construct the actual transaction and store it in the class's dict
            store
        """
        ops = list()
        for op in self.ops:
            if isinstance(op, ProposalBuilder):
                # This operation is a proposal an needs to be deal with
                # differently
                proposal = await op.get_raw()
                if proposal:
                    ops.append(proposal)
            elif isinstance(op, self.operation_class):
                ops.extend([op])
            else:
                # otherwise, we simply wrap ops into Operations
                ops.extend([self.operation_class(op)])

        # We now wrap everything into an actual transaction
        ops = await self.add_required_fees(ops, asset_id=self.fee_asset_id)
        expiration = self.get("expiration") or formatTimeFromNow(
            self.expiration
            or self.blockchain.expiration
            or 30  # defaults to 30 seconds
        )
        if not self.get("ref_block_num"):
            ref_block_num, ref_block_prefix = await self.get_block_params()
        else:
            ref_block_num = self["ref_block_num"]
            ref_block_prefix = self["ref_block_prefix"]
        self.tx = self.signed_transaction_class(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops,
        )
        dict.update(self, self.tx.json())
        self._unset_require_reconstruction()

    async def get_block_params(self, use_head_block=False):
        """ Auxiliary method to obtain ``ref_block_num`` and
            ``ref_block_prefix``. Requires a websocket connection to a
            witness node!
        """
        ws = self.blockchain.rpc
        dynBCParams = await ws.get_dynamic_global_properties()
        if use_head_block:
            ref_block_num = dynBCParams["head_block_number"] & 0xFFFF
            ref_block_prefix = struct.unpack_from(
                "<I", unhexlify(dynBCParams["head_block_id"]), 4
            )[0]
        else:
            # need to get subsequent block because block head doesn't return 'id' - stupid
            block = await ws.get_block_header(
                int(dynBCParams["last_irreversible_block_num"]) + 1
            )
            ref_block_num = dynBCParams["last_irreversible_block_num"] & 0xFFFF
            ref_block_prefix = struct.unpack_from(
                "<I", unhexlify(block["previous"]), 4
            )[0]
        return ref_block_num, ref_block_prefix

    async def sign(self):
        """ Sign a provided transaction with the provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        await self.constructTx()

        if "operations" not in self or not self["operations"]:
            return

        # Legacy compatibility!
        # If we are doing a proposal, obtain the account from the proposer_id
        if self.blockchain.proposer:
            proposer = await self.account_class(
                self.blockchain.proposer, blockchain_instance=self.blockchain
            )
            self.wifs = set()
            self.signing_accounts = list()
            await self.appendSigner(proposer["id"], "active")

        # We need to set the default prefix, otherwise pubkeys are
        # presented wrongly!
        if self.blockchain.rpc:
            self.operations.default_prefix = self.blockchain.rpc.chain_params["prefix"]
        elif "blockchain" in self:
            self.operations.default_prefix = self["blockchain"]["prefix"]

        if not any(self.wifs):
            raise MissingKeyError

        self.tx.sign(self.wifs, chain=self.blockchain.rpc.chain_params)
        self["signatures"].extend(self.tx.json().get("signatures"))
        return self.tx

    async def verify_authority(self):
        """ Verify the authority of the signed transaction
        """
        try:
            if not await self.blockchain.rpc.verify_authority(await self.json()):
                raise InsufficientAuthorityError
        except Exception as e:
            raise e

    async def broadcast(self):
        """ Broadcast a transaction to the blockchain network

            :param tx tx: Signed transaction to broadcast
        """
        # Sign if not signed
        if not self._is_signed():
            await self.sign()

        # Cannot broadcast an empty transaction
        if "operations" not in self or not self["operations"]:
            log.debug("No operations in transaction! Returning")
            return

        # Obtain JS
        ret = await self.json()

        # Debugging mode does not broadcast
        if self.blockchain.nobroadcast:
            log.warning("Not broadcasting anything!")
            self.clear()
            return ret

        # Broadcast
        try:
            if self.blockchain.blocking:
                ret = await self.blockchain.rpc.broadcast_transaction_synchronous(
                    ret, api="network_broadcast"
                )
                ret.update(**ret.get("trx", {}))
            else:
                await self.blockchain.rpc.broadcast_transaction(
                    ret, api="network_broadcast"
                )
        except Exception as e:
            raise e
        finally:
            self.clear()

        return ret

    async def addSigningInformation(self, account, permission):
        """ This is a private method that adds side information to a
            unsigned/partial transaction in order to simplify later
            signing (e.g. for multisig or coldstorage)

            FIXME: Does not work with owner keys!
        """
        self.constructTx()
        self["blockchain"] = self.blockchain.rpc.chain_params

        if isinstance(account, self.publickey_class):
            self["missing_signatures"] = [str(account)]
        else:
            accountObj = await self.account_class(account)
            authority = accountObj[permission]
            # We add a required_authorities to be able to identify
            # how to sign later. This is an array, because we
            # may later want to allow multiple operations per tx
            self.update({"required_authorities": {accountObj["name"]: authority}})
            for account_auth in authority["account_auths"]:
                account_auth_account = await self.account_class(account_auth[0])
                self["required_authorities"].update(
                    {account_auth[0]: account_auth_account.get(permission)}
                )

            # Try to resolve required signatures for offline signing
            self["missing_signatures"] = [x[0] for x in authority["key_auths"]]
            # Add one recursion of keys from account_auths:
            for account_auth in authority["account_auths"]:
                account_auth_account = await self.account_class(account_auth[0])
                self["missing_signatures"].extend(
                    [x[0] for x in account_auth_account[permission]["key_auths"]]
                )
