from binascii import hexlify, unhexlify
from calendar import timegm
from datetime import datetime
import ecdsa
import hashlib
import json
import math
import struct
import sys
import time
from .account import PublicKey, Address

#import graphenelib.address as address
#from graphenelib.base58 import base58decode,base58encode,base58CheckEncode,base58CheckDecode,btsBase58CheckEncode,btsBase58CheckDecode

reserved_spaces = {}
reserved_spaces["relative_protocol_ids"] = 0
reserved_spaces["protocol_ids"]          = 1
reserved_spaces["implementation_ids"]    = 2

object_type                        = {}
object_type["null"]                = 0
object_type["base"]                = 1
object_type["account"]             = 2
object_type["asset"]               = 3
object_type["force_settlement"]    = 4
object_type["committee_member"]    = 5
object_type["witness"]             = 6
object_type["limit_order"]         = 7
object_type["call_order"]          = 8
object_type["custom"]              = 9
object_type["proposal"]            = 10
object_type["operation_history"]   = 11
object_type["withdraw_permission"] = 12
object_type["vesting_balance"]     = 13
object_type["worker"]              = 14
object_type["balance"]             = 15
object_type["OBJECT_TYPE_COUNT"]   = 16

vote_type = {}
vote_type["committee"] = 0
vote_type["witness"]   = 1
vote_type["worker"]    = 2

operations = {}
operations["transfer"]                                  = 0
operations["limit_order_create"]                        = 1
operations["short_order_create"]                        = 2
operations["call_order_update"]                         = 3
operations["fill_order"]                                = 4
operations["account_create"]                            = 5
operations["account_update"]                            = 6
operations["account_whitelist"]                         = 7
operations["account_upgrade"]                           = 8
operations["account_transfer"]                          = 9
operations["asset_create"]                              = 10
operations["asset_update"]                              = 11
operations["asset_update_bitasset"]                     = 12
operations["asset_update_feed_producers"]               = 13
operations["asset_issue"]                               = 14
operations["asset_reserve"]                             = 15
operations["asset_fund_fee_pool"]                       = 16
operations["asset_settle"]                              = 17
operations["asset_global_settle"]                       = 18
operations["asset_publish_feed"]                        = 19
operations["witness_create"]                            = 20
operations["proposal_create"]                           = 21
operations["proposal_update"]                           = 22
operations["proposal_delete"]                           = 23
operations["withdraw_permission_create"]                = 24
operations["withdraw_permission_update"]                = 25
operations["withdraw_permission_claim"]                 = 26
operations["withdraw_permission_delete"]                = 27
operations["committee_member_create"]                   = 28
operations["committee_member_update_global_parameters"] = 29
operations["vesting_balance_create"]                    = 30
operations["vesting_balance_withdraw"]                  = 31
operations["worker_create"]                             = 32
operations["custom"]                                    = 33
operations["assert"]                                    = 34
operations["balance_claim"]                             = 35
operations["override_transfer"]                         = 36

chainid        = "<not-defined-yet>"
PREFIX         = "BTS"

## Variable encodings
def varint(n):
    data = b''
    while n >= 0x80:
        data += bytes([ (n & 0x7f) | 0x80 ])
        n >>= 7
    data += bytes([n])
    return data

def varintdecode(data):
    shift = 0
    result = 0
    for c in data:
        b = ord(c)
        result |= ((b & 0x7f) << shift)
        if not (b & 0x80):
            break
        shift += 7
    return result

def varintlength(n):
    length = 1
    while n >= 0x80:
        length += 1
        n >>= 7
    return length

def variable_buffer( s ) :
    return varint(len(s)) + s

# Variable types
class Uint8() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<B",self.data)
    def __str__(self)     : return '%d' % self.data
class Uint16() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<H",self.data)
    def __str__(self)     : return '%d' % self.data
class Uint32() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<I",self.data)
    def __str__(self)     : return '%d' % self.data
class Uint64() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<Q",self.data)
    def __str__(self)     : return '%d' % self.data
class Varint32() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return varint(self.data)
    def __str__(self)     : return '%d' % self.data
class Int64():
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<q",self.data)
    def __str__(self)     : return '%d' % self.data
class String():
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return varint(len(self.data)) + bytes(self.data,'utf-8')
    def __str__(self)     : return '%d' % str(self.data)
class Bytes():
    def __init__(self,d,length=None) :
        self.data   = d; 
        if length :
            self.length = length
        else :
            self.length = len(self.data)
    def __bytes__(self)   : return varint(self.length) + bytes(self.data, 'utf-8')
    def __str__(self)     : return str(self.data)
class Void():
    def __init__(self,d)  : raise NotImplementedError
    def __bytes__(self)   : raise NotImplementedError
    def __str__(self)     : raise NotImplementedError
class Array():
    def __init__(self,d)  : self.data = d;
    def __bytes__(self)   : return varint(len(self.data)) + b"".join([bytes(a) for a in self.data])
    def __str__(self)     : return {}.update([str(a) for a in self.data])

class Bool(Uint8): # Bool = Uint8 / FIXME verify?!
    def __init__(self,d) : 
        super().__init__(d)
class Time_point_sec(Uint32): # Time_point_sec = Uint32 / FIXME iso string!
    def __init__(self,d) : 
        super().__init__(d)
class Set(Array): # Set = Array
    def __init__(self,d) : 
        super().__init__(d)

class Fixed_array():
    def __init__(self,d)  : raise NotImplementedError
    def __bytes__(self)   : raise NotImplementedError
    def __str__(self)     : raise NotImplementedError
class Optional():
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<B",1) + bytes(self.data) if self.data else struct.pack("<B",0)
    def __str__(self)     : return str(self.data) if self.data else ''
class Static_variant():
    def __init__(self,d,type_id)  : self.data = d; self.type_id = type_id
    def __bytes__(self)   : return varint(self.type_id) + bytes(self.data)
    def __str__(self)     : return { self._type_id : str(self.data) }
class Map():
    def __init__(self,d)  : raise NotImplementedError
    def __bytes__(self)   : raise NotImplementedError
    def __str__(self)     : raise NotImplementedError

class Id():
    def __init__(self,d)  : self.data = Varint32(d)
    def __bytes__(self)   : return bytes(self.data)
    def __str__(self)     : return str(self.data)

def JsonObj(data):
    return json.loads(str(data))

# Graphene objects
from collections import OrderedDict
class GrapheneObject(object) :
    def __init__(self, data):
        self.data = data 
    def __bytes__(self):
        b = b""
        for name, value in self.data.items():
            if isinstance(value, str) :
                 b += bytes(value,'utf-8')
            else :
                 b += bytes(value)
        return b
    def __json__(self) :
        d = {} ## JSON output is *not* ordered
        for name, value in self.data.items():
            if isinstance(value, GrapheneObject) :
                d.update( { name : value.__json__() } )
            elif isinstance(value, Optional) :
                d.update( { name : json.loads(str(value)) } )
            else :
                d.update( { name : str(value) } )
        return OrderedDict(d)
    def __str__(self) :
        return json.dumps(self.__json__())

class Object_id_type():
    pass

class Vote_id():
    pass

class Protocol_id_type() :
    def __init__(self, _type, instance) :
        self._type   = _type
        self.space   = reserved_spaces["protocol_ids"]
        self.obj     = object_type[_type]
        self.instance = Id(instance)
        self.Id      = "%d.%d.%d"%(self.space,self.obj,instance)
    def __bytes__(self):
        return bytes(self.instance)  # only yield instance
    def __str__(self) :
        return self.Id

class Asset(GrapheneObject) :
    def __init__(self, _amount, _asset_id):
        super().__init__(OrderedDict([
                       ('amount',   Uint64(_amount)),
                       ('asset_id', Protocol_id_type("asset",_asset_id) )
                    ]))

class Memo(GrapheneObject) :
    def __init__(self, _from, _to, _nonce, _message):
        super().__init__(OrderedDict([
                       ('from',    PublicKey(_from, prefix="BTS")),
                       ('to',      PublicKey(_to, prefix="BTS")),
                       ('nonce',   Uint64(_nonce)),
                       ('message', Bytes(_message))
                     ]))

class Transfer(GrapheneObject) :
    def __init__(self, _feeObj, _from, _to, _amountObj, _memo=None):
        super().__init__(OrderedDict([
                      ('fee'       , _feeObj),
                      ('from'      , Protocol_id_type("account",_from)),
                      ('to'        , Protocol_id_type("account",_to)),
                      ('amount'    , _amountObj),
                      ('memo'      , Optional(_memo))
                    ]))  ## FIXME missing future_extensions

class Transaction(GrapheneObject) :
    def __init__(self, refNum, refPrefix, expiration, operations):
        super().__init__(OrderedDict([
                      ('ref_block_num', Uint16(refNum)),
                      ('ref_block_prefix', Uint32(refPrefix)),
                      ('expiration', Time_point_sec(expiration)),
                      ('operations', Array(operations))
                    ]))  ## FIXME missing future_extensions

class Signed_Transaction(GrapheneObject) :
    def __init__(self, refNum, refPrefix, expiration, operations):
        super().__init__(OrderedDict([
                      ('ref_block_num', Uint16(refNum)),
                      ('ref_block_prefix', Uint32(refPrefix)),
                      ('expiration', Time_point_sec(expiration)),
                      ('operations', Array(operations)),
                      ('signatures', Array([ Bytes(s,65) for s in signatures]))
                    ]))  ## FIXME missing future_extensions

if __name__ == '__main__':
    fee      = Asset(10, 15)
    amount   = Asset(1000000, 15)
    memo     = Memo("BTS774RSm2rJuktBbv9BUh7hj7WHsSXjviW16yy21qmtp7YAzK87L", "BTS774RSm2rJuktBbv9BUh7hj7WHsSXjviW16yy21qmtp7YAzK87L", 1244, "Foobar")
    transfer = Transfer(fee, 8, 10, amount, memo)

    print(json.dumps(json.loads(str(transfer)),indent=4))
    print(hexlify(bytes(transfer)))
