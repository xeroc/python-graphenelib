from .types import *
from .chains import known_chains
from .objecttypes import object_type
from .account import PublicKey
from .chains import default_prefix


class GrapheneObject(object) :
    """ Core abstraction class

        This class is used for any JSON reflected object in Graphene.

        * ``instance.__json__()`` : encodes data into json format
        * ``bytes(instance)`` : encodes data into wire format
        * ``str(instances)`` : dumps json object as string

    """
    def __init__(self, data=None) :
        self.data = data

    def __bytes__(self) :
        if self.data is None :
            return bytes()
        b = b""
        for name, value in self.data.items() :
            if isinstance(value, str) :
                b += bytes(value, 'utf-8')
            else :
                b += bytes(value)
        return b

    def __json__(self) :
        if self.data is None :
            return {}
        d = {}  # JSON output is *not* ordered
        for name, value in self.data.items() :
            if isinstance(value, Optional) and value.isempty() :
                continue

            if isinstance(value, String) :
                d.update({name: str(value)})
            else:
                try :
                    d.update({name : JsonObj(value)})
                except :
                    d.update({name : value.__str__()})
        return d

    def __str__(self) :
        return json.dumps(self.__json__())

    def toJson(self):
        return self.__json__()

    def json(self):
        return self.__json__()


def isArgsThisClass(self, args):
    return (len(args) == 1 and type(args[0]).__name__ == type(self).__name__)

"""
    Actual Objects
"""


class Asset(GrapheneObject) :
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('amount',   Int64(kwargs["amount"])),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset"))
            ]))


class Memo(GrapheneObject) :
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "message" in kwargs and kwargs["message"] :
                if "chain" not in kwargs:
                    chain = "BTS"
                else:
                    chain = kwargs["chain"]
                if isinstance(chain, str) and chain in known_chains :
                    chain_params = known_chains[chain]
                elif isinstance(chain, dict) :
                    chain_params = chain
                else :
                    raise Exception("Memo() only takes a string or a dict as chain!")
                if "prefix" not in chain_params :
                    raise Exception("Memo() needs a 'prefix' in chain params!")
                prefix = chain_params["prefix"]
                super().__init__(OrderedDict([
                    ('from',    PublicKey(kwargs["from"], prefix=prefix)),
                    ('to',      PublicKey(kwargs["to"], prefix=prefix)),
                    ('nonce',   Uint64(int(kwargs["nonce"]))),
                    ('message', Bytes(kwargs["message"]))
                ]))
            else :
                super().__init__(None)


class Price(GrapheneObject):
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('base', Asset(kwargs["base"])),
                ('quote', Asset(kwargs["quote"]))
            ]))


class PriceFeed(GrapheneObject):
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('settlement_price', Price(kwargs["settlement_price"])),
                ('maintenance_collateral_ratio', Uint16(kwargs["maintenance_collateral_ratio"])),
                ('maximum_short_squeeze_ratio', Uint16(kwargs["maximum_short_squeeze_ratio"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
            ]))


class Permission(GrapheneObject):
    def __init__(self, *args, **kwargs) :
        # Allow for overwrite of prefix
        prefix = kwargs.pop("prefix", default_prefix)

        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            # Sort keys (FIXME: ideally, the sorting is part of Public
            # Key and not located here)
            kwargs["key_auths"] = sorted(
                kwargs["key_auths"],
                key=lambda x: repr(PublicKey(x[0], prefix=prefix).address),
                reverse=False,
            )
            accountAuths = Map([
                [String(e[0]), Uint16(e[1])]
                for e in kwargs["account_auths"]
            ])
            keyAuths = Map([
                [PublicKey(e[0], prefix=prefix), Uint16(e[1])]
                for e in kwargs["key_auths"]
            ])
            super().__init__(OrderedDict([
                ('weight_threshold', Uint32(int(kwargs["weight_threshold"]))),
                ('account_auths'   , accountAuths),
                ('key_auths'       , keyAuths),
                ('extensions'      , Set([])),
            ]))


class AccountOptions(GrapheneObject) :
    def __init__(self, *args, **kwargs) :
        # Allow for overwrite of prefix
        prefix = kwargs.pop("prefix", default_prefix)

        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('memo_key'         , PublicKey(kwargs["memo_key"], prefix=prefix)),
                ('voting_account'   , ObjectId(kwargs["voting_account"], "account")),
                ('num_witness'      , Uint16(kwargs["num_witness"])),
                ('num_committee'    , Uint16(kwargs["num_committee"])),
                ('votes'            , Array([VoteId(o) for o in kwargs["votes"]])),
                ('extensions'       , Set([])),
            ]))


class AssetOptions(GrapheneObject) :
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('max_supply', Uint64(kwargs["max_supply"])),
                ('market_fee_percent', Uint16(kwargs["market_fee_percent"])),
                ('max_market_fee', Uint64(kwargs["max_market_fee"])),
                ('issuer_permissions', Uint16(kwargs["issuer_permissions"])),
                ('flags', Uint16(kwargs["flags"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
                ('whitelist_authorities',
                    Array([ObjectId(o, "account") for o in kwargs["whitelist_authorities"]])),
                ('blacklist_authorities',
                    Array([ObjectId(o, "account") for o in kwargs["blacklist_authorities"]])),
                ('whitelist_markets',
                    Array([ObjectId(o, "asset") for o in kwargs["whitelist_markets"]])),
                ('blacklist_markets',
                    Array([ObjectId(o, "asset") for o in kwargs["blacklist_markets"]])),
                ('description', String(kwargs["description"])),
                ('extensions', Set([])),
            ]))
