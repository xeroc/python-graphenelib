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
class Varint32() :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return varint(self.data)
    def __str__(self)     : return '%d' % self.data

class Uint64(object) :
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<Q",self.data)
    def __str__(self)     : return '%d' % self.data

class Id():
    def __init__(self,d)  : self.data = Varint32(d)
    def __bytes__(self)   : return bytes(self.data)
    def __str__(self)     : return str(self.data)

def JsonObj(data):
    return json.loads(str(data))

# Format 	  C Type 	Python type 	Standard size 	Notes
# x 	pad byte 	no value 	  	 
# c 	char 	string of length 1 	1 	 
# b 	signed char 	integer 	1 	(3)
# B 	unsigned char 	integer 	1 	(3)
# ? 	_Bool 	bool 	1 	(1)
# h 	short 	integer 	2 	(3)
# H 	unsigned short 	integer 	2 	(3)
# i 	int 	integer 	4 	(3)
# I 	unsigned int 	integer 	4 	(3)
# l 	long 	integer 	4 	(3)
# L 	unsigned long 	integer 	4 	(3)
# q 	long long 	integer 	8 	(2), (3)
# Q 	unsigned long long 	integer 	8 	(2), (3)
# f 	float 	float 	4 	(4)
# d 	double 	float 	8 	(4)
# s 	char[] 	string 	  	 
# p 	char[] 	string 	  	 
# P 	void* 	integer 	  	(5), (3)

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
            else :
                d.update( { name : str(value) } )
        return OrderedDict(d)
    def __str__(self) :
        return json.dumps(self.__json__())

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
    def __init__(self, _amount, _asset):
        super().__init__(OrderedDict([
                       ('amount',   Uint64(_amount)),
                       ('asset_id', _asset)
                    ]))

class Memo(GrapheneObject) :
    def __init__(self, _from, _to, _nonce, _message):
        super().__init__(OrderedDict([
                       ('from',    _from),
                       ('to',      _to),
                       ('nonce',   Uint64(_nonce)),
                       ('message', _message)
                     ]))

class Transfer(GrapheneObject) :
    def __init__(self, _fee, _from, _to, _amount, _memo):
        super().__init__(OrderedDict([
                      ('fee'    , _fee),
                      ('from'   , _from),
                      ('to'     , _to),
                      ('amount' , _amount),
                      ('memo'   , _memo)
                    ]))

asset_id = Protocol_id_type("asset", 15)
fee      = Asset(10, asset_id)
amount   = Asset(1000000, asset_id)
_from    = Protocol_id_type("account", 8)
to       = Protocol_id_type("account", 10)
memo     = Memo(_from, to, 1244, b"Foobar")
transfer = Transfer(fee, _from, to, amount, memo)

print(json.dumps(json.loads(str(transfer)),indent=4))
print(hexlify(bytes(transfer)))
print(b"0a000000000000000f080a40420f00000000000f080adc04000000000000466f6f626172")
