# -*- coding: utf-8 -*-
from .blockchainobject import BlockchainObject
from .exceptions import GenesisBalanceDoesNotExistsException, MissingKeyError
from .instance import AbstractBlockchainInstanceProvider


class GenesisBalance(BlockchainObject, AbstractBlockchainInstanceProvider):
    """ Deals with Assets of the network.

        :param str Asset: Symbol name or object id of an asset
        :param bool lazy: Lazy loading
        :param bool full: Also obtain bitasset-data and dynamic asset data
        :param instance blockchain_instance: instance to use when accesing a RPC
        :returns: All data of an asset
        :rtype: dict

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Asset.refresh()``.
    """

    def __init__(self, *args, **kwargs):
        self.define_classes()
        assert self.type_id
        assert self.account_class
        assert self.operations
        assert self.address_class
        assert self.publickey_class

        self.full = kwargs.pop("full", False)
        BlockchainObject.__init__(self, *args, **kwargs)

    def refresh(self):
        balance = self.blockchain.rpc.get_object(self.identifier)
        if not balance:
            raise GenesisBalanceDoesNotExistsException
        super(GenesisBalance, self).__init__(
            balance, blockchain_instance=self.blockchain
        )

    def claim(self, account=None, **kwargs):
        """ Claim a balance from the genesis block

            :param str balance_id: The identifier that identifies the balance
                to claim (1.15.x)
            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = self.account_class(account)
        pubkeys = self.blockchain.wallet.getPublicKeys()
        addresses = dict()
        for p in pubkeys:
            pubkey = self.publickey_class(p)
            addresses[
                str(self.address_class.from_pubkey(pubkey, compressed=False, version=0))
            ] = pubkey
            addresses[
                str(self.address_class.from_pubkey(pubkey, compressed=True, version=0))
            ] = pubkey
            addresses[
                str(
                    self.address_class.from_pubkey(pubkey, compressed=False, version=56)
                )
            ] = pubkey
            addresses[
                str(self.address_class.from_pubkey(pubkey, compressed=True, version=56))
            ] = pubkey

        if self["owner"] not in addresses.keys():
            raise MissingKeyError("Need key for address {}".format(self["owner"]))

        op = self.operations.Balance_claim(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "deposit_to_account": account["id"],
                "balance_to_claim": self["id"],
                "balance_owner_key": addresses[self["owner"]],
                "total_claimed": self["balance"],
                "prefix": self.blockchain.prefix,
            }
        )
        signers = [
            account["name"],  # The fee payer and receiver account
            addresses.get(self["owner"]),  # The genesis balance!
        ]
        return self.blockchain.finalizeOp(op, signers, "active", **kwargs)


class GenesisBalances(list, AbstractBlockchainInstanceProvider):
    """ List genesis balances that can be claimed from the
        keys in the wallet
    """

    def __init__(self, **kwargs):
        self.define_classes()
        assert self.genesisbalance_class
        assert self.publickey_class
        assert self.address_class

        pubkeys = self.blockchain.wallet.getPublicKeys()
        addresses = list()
        for p in pubkeys:
            pubkey = self.publickey_class(p)
            addresses.append(
                str(self.address_class.from_pubkey(pubkey, compressed=False, version=0))
            )
            addresses.append(
                str(self.address_class.from_pubkey(pubkey, compressed=True, version=0))
            )
            addresses.append(
                str(
                    self.address_class.from_pubkey(pubkey, compressed=False, version=56)
                )
            )
            addresses.append(
                str(self.address_class.from_pubkey(pubkey, compressed=True, version=56))
            )

        balancess = self.blockchain.rpc.get_balance_objects(addresses)

        super(GenesisBalances, self).__init__(
            [
                self.genesisbalance_class(
                    x, **kwargs, blockchain_instance=self.blockchain
                )
                for x in balancess
            ]
        )
