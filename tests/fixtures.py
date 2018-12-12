import os
import mock
import yaml

# Graphene API
from grapheneapi import exceptions
from grapheneapi.api import Api, Websocket, Http

# Graphenebase
import graphenebase.ecdsa as ecdsa
from graphenebase.aes import AESCipher
from graphenebase.base58 import (
    Base58,
    base58decode,
    base58encode,
    ripemd160,
    base58CheckEncode,
    base58CheckDecode,
    gphBase58CheckEncode,
    gphBase58CheckDecode,
    b58decode,
    b58encode
)
from graphenebase import types, utils
from graphenebase.transactions import (
    formatTimeFromNow,
    timeformat
)
from graphenebase.operations import Account_create
from graphenebase.signedtransactions import (
    Signed_Transaction,
    MissingSignatureForKey
)
from graphenebase.account import (
    BrainKey,
    Address,
    PublicKey,
    PrivateKey,
    PasswordKey,
    GrapheneAddress,
    BitcoinAddress
)
from graphenebase.objects import (
    Operation,
    GrapheneObject
)
from graphenebase.operations import (
    Newdemooepration,
    Newdemooepration2,
    Demooepration
)
from graphenebase.operationids import (
    ops,
    operations,
    getOperationNameForId
)

from graphenebase import bip38
from graphenebase.bip38 import encrypt, decrypt
from graphenebase.transactions import getBlockParams

# Graphenestorage
from graphenestorage.exceptions import (
    WrongMasterPasswordException,
    KeyAlreadyInStoreException,
    WalletLocked
)
import graphenestorage as storage
from graphenestorage.interfaces import (
    StoreInterface,
    KeyInterface,
    ConfigInterface,
    EncryptedKeyInterface,
)
from graphenestorage.sqlite import SQLiteStore


# Common stuff

from graphenecommon.instance import BlockchainInstance as GBlockchainInstance
from graphenecommon.amount import Amount as GAmount
from graphenecommon.account import (
    Account as GAccount,
    AccountUpdate as GAccountUpdate
)
from graphenecommon.asset import Asset as GAsset
from graphenecommon.committee import Committee as GCommittee


class Chain:
    def __init__(self, *args, **kwargs):
        pass

    @property
    def rpc(self):
        """ We are patching rpc similar to a regular RPC
            connection. However, it will always return
            an empty object!
        """
        class RPC:
            def get_objects(self, *args, **kwargs):
                return []

            def get_object(self, *args, **kwargs):
                return {}

            def get_account_history(self, *args, **kwargs):
                return []

            def lookup_account_names(self, *args, **kwargs):
                return [None]

            def __getattr__(self, name):
                def fun(self, *args, **kwargs):
                    return {}
                return fun
        return RPC()

    def upgrade_account(self, *args, **kwargs):
        pass


class BlockchainInstance(GBlockchainInstance):
    def get_instance_class(self):
        return Chain


@BlockchainInstance.inject
class Asset(GAsset):
    type_id = 3


@BlockchainInstance.inject
class Amount(GAmount):
    asset_class = Asset


@BlockchainInstance.inject
class Account(GAccount):
    type_id = 2
    amount_class = Amount
    operations = operations


@BlockchainInstance.inject
class AccountUpdate(GAccountUpdate):
    account_class = Account


@BlockchainInstance.inject
class Committee(GCommittee):
    type_id = 5
    account_class = Account


def fixture_data():
    with open(os.path.join(os.path.dirname(__file__), "fixtures.yaml")) as fid:
        data = yaml.safe_load(fid)

    # Feed our objects into the caches!
    for account in data.get("accounts"):
        Account._cache[account["id"]] = account
        Account._cache[account["name"]] = account

    for asset in data.get("assets"):
        Asset._cache[asset["symbol"]] = asset
        Asset._cache[asset["id"]] = asset

    for committee in data.get("committees"):
        Committee._cache[committee["id"]] = committee
