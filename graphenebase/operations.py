# -*- coding: utf-8 -*-
from collections import OrderedDict
from .types import (
    Uint16,
    Uint32,
    Int64,
    String,
    Array,
    Set,
    Optional,
    Map,
    VoteId,
    ObjectId,
)
from .objects import GrapheneObject, isArgsThisClass
from .account import PublicKey
from .chains import default_prefix


# Old style of defining an operation
class Demooepration(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):  # pragma: no cover
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]  # pragma: no cover
            super().__init__(
                OrderedDict(
                    [("string", String(kwargs["string"])), ("extensions", Set([]))]
                )
            )


# New style of defining operation
class Newdemooepration(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("string", String(kwargs["string"])),
                ("optional", Optional(String(kwargs.get("optional")))),
                ("extensions", Set([])),
            ]
        )


class Newdemooepration2(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                # Different order
                ("optional", Optional(String(kwargs.get("optional")))),
                ("string", String(kwargs["string"])),
                ("extensions", Set([])),
            ]
        )


class Asset(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("amount", Int64(kwargs["amount"])),
                ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
            ]
        )


class Permission(GrapheneObject):
    def detail(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", default_prefix)
        kwargs["key_auths"] = sorted(
            kwargs["key_auths"],
            key=lambda x: PublicKey(x[0], prefix=prefix),
            reverse=False,
        )
        accountAuths = Map(
            [[ObjectId(e[0], "account"), Uint16(e[1])] for e in kwargs["account_auths"]]
        )
        keyAuths = Map(
            [
                [PublicKey(e[0], prefix=prefix), Uint16(e[1])]
                for e in kwargs["key_auths"]
            ]
        )
        return OrderedDict(
            [
                ("weight_threshold", Uint32(int(kwargs["weight_threshold"]))),
                ("account_auths", accountAuths),
                ("key_auths", keyAuths),
                ("extensions", Set([])),
            ]
        )


class AccountOptions(GrapheneObject):
    def detail(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", default_prefix)
        # remove dublicates
        kwargs["votes"] = list(set(kwargs["votes"]))
        """ This is an example how to sort votes prior to using them in the
            Object
        """
        # # Sort votes
        # kwargs["votes"] = sorted(
        #     kwargs["votes"],
        #     key=lambda x: float(x.split(":")[1]),
        # )
        return OrderedDict(
            [
                ("memo_key", PublicKey(kwargs["memo_key"], prefix=prefix)),
                ("voting_account", ObjectId(kwargs["voting_account"], "account")),
                ("num_witness", Uint16(kwargs["num_witness"])),
                ("num_committee", Uint16(kwargs["num_committee"])),
                ("votes", Array([VoteId(o) for o in kwargs["votes"]])),
                ("extensions", Set([])),
            ]
        )


# For more detailed unit testing
class Account_create(GrapheneObject):
    def detail(self, *args, **kwargs):
        prefix = kwargs.get("prefix", default_prefix)
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("registrar", ObjectId(kwargs["registrar"], "account")),
                ("referrer", ObjectId(kwargs["referrer"], "account")),
                ("referrer_percent", Uint16(kwargs["referrer_percent"])),
                ("name", String(kwargs["name"])),
                ("owner", Permission(kwargs["owner"], prefix=prefix)),
                ("active", Permission(kwargs["active"], prefix=prefix)),
                ("options", AccountOptions(kwargs["options"], prefix=prefix)),
                ("extensions", Set([])),
            ]
        )
