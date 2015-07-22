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

object_type                        = {}
object_type["null"]                = 0
object_type["base"]                = 1
object_type["key"]                 = 2
object_type["account"]             = 3
object_type["asset"]               = 4
object_type["force_settlement"]    = 5
object_type["delegate"]            = 6
object_type["witness"]             = 7
object_type["limit_order"]         = 8
object_type["short_order"]         = 9
object_type["call_order"]          = 10
object_type["custom"]              = 11
object_type["proposal"]            = 12
object_type["operation_history"]   = 13
object_type["withdraw_permission"] = 14
object_type["bond_offer"]          = 15
object_type["bond"]                = 16
object_type["file"]                = 17
object_type["OBJECT_TYPE_COUNT"]   = 18

operations = {}
operations["transfer"]                    = 0
operations["limit_order_create"]          = 1
operations["short_order_create"]          = 2
operations["limit_order_cancel"]          = 3
operations["short_order_cancel"]          = 4
operations["call_order_update"]           = 5
operations["key_create"]                  = 6
operations["account_create"]              = 7
operations["account_update"]              = 8
operations["account_whitelist"]           = 9
operations["account_transfer"]            = 10
operations["asset_create"]                = 11
operations["asset_update"]                = 12
operations["asset_update_bitasset"]       = 13
operations["asset_update_feed_producers"] = 14
operations["asset_issue"]                 = 15
operations["asset_burn"]                  = 16
operations["asset_fund_fee_pool"]         = 17
operations["asset_settle"]                = 18
operations["asset_global_settle"]         = 19
operations["asset_publish_feed"]          = 20
operations["delegate_create"]             = 21
operations["witness_create"]              = 22
operations["witness_withdraw_pay"]        = 23
operations["proposal_create"]             = 24
operations["proposal_update"]             = 25
operations["proposal_delete"]             = 26
operations["withdraw_permission_create"]  = 27
operations["withdraw_permission_update"]  = 28
operations["withdraw_permission_claim"]   = 29
operations["withdraw_permission_delete"]  = 30
operations["fill_order"]                  = 31
operations["global_parameters_update"]    = 32
operations["file_write"]                  = 33
operations["vesting_balance_create"]      = 34
operations["vesting_balance_withdraw"]    = 35
operations["bond_create_offer"]           = 36
operations["bond_cancel_offer"]           = 37
operations["bond_accept_offer"]           = 38
operations["bond_claim_collateral"]       = 39
operations["worker_create"]               = 40
operations["custom"]                      = 41

reserved_spaces = {}
reserved_spaces["relative_protocol_ids"] = 0
reserved_spaces["protocol_ids"]          = 1
reserved_spaces["implementation_ids"]    = 2
reserved_spaces["RESERVE_SPACES_COUNT"]  = 3

chainid        = "75c11a81b7670bbaa721cc603eadb2313756f94a3bcbb9928e9101432701ac5f"
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
from collections import OrderedDict as oDict
class GrapheneObject(object) :
    def __init__(self, **kwargs):
        self.data = oDict()
        for name, value in kwargs.items():
            self.data[name] = value
    def __bytes__(self):
        b = b""
        for d in self.data.values() :
            if isinstance(d,str) :
                 b += bytes(d,'utf-8')
            else :
                 b += bytes(d)
        return b
    def __json__(self) :
        d = {}
        for name, value in self.data.items():
            if isinstance(value, GrapheneObject) :
                d[ name ] = value.__json__()
            else :
                d[ name ] = str(value)
        return d
    def __str__(self) :
        return json.dumps(self.__json__())

class Protocol_id_type() :
    def __init__(self, _type, _object) :
        self._type   = _type
        self._object = Id(_object)
        self.Id      = "%d.%d.%d"%(reserved_spaces["protocol_ids"],object_type[_type],_object)
        #super().__init__(**{'id':self.Id})
    def __bytes__(self):
        return bytes(self._object)
    def __str__(self) :
        return self.Id

class Asset(GrapheneObject) :
    def __init__(self, _amount, _asset):
        super().__init__(**{'amount':Uint64(_amount), 'asset_id':_asset})

class Memo(GrapheneObject) :
    def __init__(self, _from, _to, _nonce, _message):
        super().__init__(**{'from':_from, 'to':_to, 'nonce':Uint64(_nonce), 'message':_message})

class Transfer(GrapheneObject) :
    def __init__(self, _fee, _from, _to, _amount, _memo):
        super().__init__(**{'fee':_fee, 'from':_from, 'to':_to, 'amount':_amount, 'memo':_memo})

asset_id = Protocol_id_type("asset", 15)
fee      = Asset(10, asset_id)
amount   = Asset(1000000, asset_id)
_from    = Protocol_id_type("key", 8)
to       = Protocol_id_type("key", 10)
memo     = Memo(_from,to,1244,b"Foobar")
transfer = Transfer(fee, _from, to, amount, memo)


print(bytes(asset_id))
print(bytes(fee     ))
print(bytes(amount  ))
print(bytes(_from   ))
print(bytes(to      ))
print(bytes(memo    ))
print(bytes(transfer))




print(json.dumps(json.loads(str(transfer)),indent=4))

print(hexlify(bytes(transfer)))
