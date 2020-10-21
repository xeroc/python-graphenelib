# -*- coding: utf-8 -*-
import os
import mock
import yaml
import json

# Graphene API
from grapheneapi import exceptions
from grapheneapi.aio.api import Api, Websocket, Http

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
    b58encode,
)
from graphenebase import types, utils
from graphenebase.transactions import formatTimeFromNow, timeformat
from graphenebase.signedtransactions import Signed_Transaction, MissingSignatureForKey
from graphenebase.account import (
    BrainKey,
    Address,
    PublicKey,
    PrivateKey,
    PasswordKey,
    GrapheneAddress,
    BitcoinAddress,
)
from graphenebase.objects import Operation, GrapheneObject
from graphenebase.operations import (
    Newdemooepration,
    Newdemooepration2,
    Demooepration,
    Account_create,
)
from graphenebase import operations as operations_module, operationids
from graphenebase.operationids import (
    ops,
    getOperationNameForId,
    getOperationName,
    operations,
)

from graphenebase import bip38
from graphenebase.bip38 import encrypt, decrypt
from graphenebase.transactions import getBlockParams

# Graphenestorage
from graphenestorage.exceptions import (
    WrongMasterPasswordException,
    KeyAlreadyInStoreException,
    WalletLocked,
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

from graphenecommon.instance import BlockchainInstance as SyncGBlockchainInstance
from graphenecommon.aio.instance import BlockchainInstance as GBlockchainInstance
from graphenecommon.instance import SharedInstance as GSharedInstance
from graphenecommon.aio.amount import Amount as GAmount
from graphenecommon.aio.account import (
    Account as GAccount,
    AccountUpdate as GAccountUpdate,
)
from graphenecommon.aio.asset import Asset as GAsset
from graphenecommon.aio.committee import Committee as GCommittee
from graphenecommon.aio.block import Block as GBlock, BlockHeader as GBlockHeader
from graphenecommon.blockchain import Blockchain as GBLockchain
from graphenecommon.aio.message import (
    Message as GMessage,
    MessageV1 as GMessageV1,
    MessageV2 as GMessageV2,
)
from graphenecommon.blockchainobject import ObjectCacheInMemory
from graphenecommon.aio.blockchainobject import BlockchainObject
from graphenecommon.aio.price import Price as GPrice
from graphenecommon.aio.wallet import Wallet as GWallet
from graphenecommon.aio.worker import Worker as GWorker, Workers as GWorkers
from graphenecommon.aio.witness import Witness as GWitness, Witnesses as GWitnesss
from graphenecommon.aio.chain import AbstractGrapheneChain

objects_cache = dict()


def store_test_object(o):
    global objects_cache
    if o.get("id"):
        objects_cache[o["id"]] = o


def get_object(id):
    return objects_cache.get(id, {})


class SharedInstance(GSharedInstance):
    pass


class Chain(AbstractGrapheneChain):
    prefix = "GPH"

    def __init__(self, *args, **kwargs):
        self.config = storage.InRamConfigurationStore()
        self.blockchainobject_class = BlockchainObject

    def is_connected(self):
        return True

    @property
    def wallet(self):
        return Wallet(keys=["5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"])

    async def info(self):
        # returns demo data
        return {
            "accounts_registered_this_interval": 18,
            "current_aslot": 33206892,
            "current_witness": "1.6.105",
            "dynamic_flags": 0,
            "head_block_id": "01f82b16db7ae25a4b9706b36c259438a9d4c8d1",
            "head_block_number": 33041174,
            "id": "2.1.0",
            "last_budget_time": "2018-12-12T10:00:00",
            "last_irreversible_block_num": 33041151,
            "next_maintenance_time": "2018-12-12T11:00:00",
            "recent_slots_filled": "340282366920938463463374607431768211455",
            "recently_missed_count": 0,
            "time": "2018-12-12T10:44:15",
            "witness_budget": 31800000,
        }

    @property
    def rpc(self):
        """ We are patching rpc similar to a regular RPC
            connection. However, it will always return
            an empty object!
        """

        class RPC:
            def _load(self, name):
                with open(
                    os.path.join(os.path.dirname(__file__), "fixtures.yaml")
                ) as fid:
                    d = yaml.safe_load(fid)
                return d.get(name)

            async def get_objects(self, ids, *args, **kwargs):
                return [await self.get_object(x) for x in ids]

            async def get_object(self, id, *args, **kwargs):
                return get_object(id)

            async def get_asset(self, name, **kwargs):
                """ Method from python-bitshares
                """
                if len(name.split(".")) == 3:
                    result = await self.get_objects([name], **kwargs)
                    return result[0]
                else:
                    return self.lookup_asset_symbols([name], **kwargs)[0]

            def lookup_asset_symbols(self, name: list, **kwargs):
                name = name[0]
                result = [
                    obj
                    for obj in objects_cache
                    if "symbol" in obj and obj["symbol"] == name
                ]
                if not result:
                    result = [None]
                return result

            async def get_account_history(self, *args, **kwargs):
                with open(
                    os.path.join(
                        os.path.dirname(__file__), "vector_get_account_history.yaml"
                    )
                ) as fid:
                    history = yaml.safe_load(fid)
                    return history

            async def get_account_balances(self, account, *args, **kwargs):
                return [{"asset_id": "1.3.0", "amount": 132442}]

            async def lookup_account_names(self, name, **kwargs):
                return [None]

            async def get_all_workers(self):
                return self._load("workers")

            async def get_workers_by_account(self, name):
                return [self._load("workers")[0]]

            def get_dynamic_global_properties(self):
                return {
                    "head_block_id": "021dcf4a9af758e508364f16e3ab5ac928b7f76c",
                    "head_block_number": 35508042,
                }

            def __getattr__(self, name):
                async def fun(self, *args, **kwargs):
                    return {}

                return fun

        return RPC()

    async def upgrade_account(self, *args, **kwargs):
        pass


class BlockchainInstance(GBlockchainInstance):
    def get_instance_class(self):
        return Chain


class SyncBlockchainInstance(SyncGBlockchainInstance):
    def get_instance_class(self):
        return Chain


@BlockchainInstance.inject
class Asset(GAsset):
    def define_classes(self):
        self.type_id = 3


@BlockchainInstance.inject
class Amount(GAmount):
    def define_classes(self):
        self.asset_class = Asset
        self.price_class = Price


@BlockchainInstance.inject
class Account(GAccount):
    def define_classes(self):
        self.type_id = 2
        self.amount_class = Amount
        self.operations = operations_module


@BlockchainInstance.inject
class AccountUpdate(GAccountUpdate):
    def define_classes(self):
        self.account_class = Account


@BlockchainInstance.inject
class Committee(GCommittee):
    def define_classes(self):
        self.type_id = 5
        self.account_class = Account


@BlockchainInstance.inject
class Block(GBlock):
    def define_classes(self):
        pass


@BlockchainInstance.inject
class BlockHeader(GBlockHeader):
    def define_classes(self):
        pass


@BlockchainInstance.inject
class Message(GMessage):
    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey


@BlockchainInstance.inject
class MessageV1(GMessageV1):
    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey


@BlockchainInstance.inject
class MessageV2(GMessageV2):
    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey


@BlockchainInstance.inject
class Price(GPrice):
    def define_classes(self):
        self.asset_class = Asset
        self.amount_class = Amount


@BlockchainInstance.inject
class Blockchain(GBLockchain):
    def define_classes(self):
        self.block_class = Block
        self.operationids = operationids


# Wallet class should use synchronous instance to initialize
@SyncBlockchainInstance.inject
class Wallet(GWallet):
    def define_classes(self):
        self.default_key_store_app_name = "graphene"
        self.privatekey_class = PrivateKey


@BlockchainInstance.inject
class Worker(GWorker):
    def define_classes(self):
        self.type_id = 14
        self.account_class = Account


@BlockchainInstance.inject
class Workers(GWorkers):
    def define_classes(self):
        self.worker_class = Worker
        self.account_class = Account


@BlockchainInstance.inject
class Witness(GWitness):
    def define_classes(self):
        self.type_id = 6
        self.account_class = Account


@BlockchainInstance.inject
class Witnesses(GWitnesss):
    def define_classes(self):
        self.witness_class = Witness
        self.account_class = Account


def fixture_data():
    with open(os.path.join(os.path.dirname(__file__), "fixtures.yaml")) as fid:
        data = yaml.safe_load(fid)

    for o in data.get("objects"):
        store_test_object(o)

    # Feed our objects into the caches!
    for account in data.get("accounts"):
        store_test_object(account)
        Account._cache[account["id"]] = account
        Account._cache[account["name"]] = account

    for asset in data.get("assets"):
        store_test_object(asset)
        Asset._cache[asset["symbol"]] = asset
        Asset._cache[asset["id"]] = asset

    for committee in data.get("committees"):
        store_test_object(committee)
        Committee._cache[committee["id"]] = committee

    for blocknum, block in data.get("blocks").items():
        block["id"] = blocknum
        Block._cache[str(blocknum)] = block

    for worker in data.get("workers"):
        store_test_object(worker)
        Worker._cache[worker["id"]] = worker

    for witness in data.get("witnesses"):
        store_test_object(witness)
        Witness._cache[witness["id"]] = witness
