from .types import *
from .chains import known_chains
from .objecttypes import object_type
from .account import PublicKey


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
                    d.update({name : str(value)})
        return OrderedDict(d)

    def __str__(self) :
        return json.dumps(self.__json__())

    def toJson(self):
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
