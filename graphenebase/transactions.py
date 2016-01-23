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
from .account import PrivateKey, PublicKey, Address

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

# :'<,'>s/    /operations["/
# :'<,'>s/: /"] = /
operations = {}
operations["transfer"] = 0
operations["limit_order_create"] = 1
operations["limit_order_cancel"] = 2
operations["call_order_update"] = 3
operations["fill_order"] = 4
operations["account_create"] = 5
operations["account_update"] = 6
operations["account_whitelist"] = 7
operations["account_upgrade"] = 8
operations["account_transfer"] = 9
operations["asset_create"] = 10
operations["asset_update"] = 11
operations["asset_update_bitasset"] = 12
operations["asset_update_feed_producers"] = 13
operations["asset_issue"] = 14
operations["asset_reserve"] = 15
operations["asset_fund_fee_pool"] = 16
operations["asset_settle"] = 17
operations["asset_global_settle"] = 18
operations["asset_publish_feed"] = 19
operations["witness_create"] = 20
operations["witness_update"] = 21
operations["proposal_create"] = 22
operations["proposal_update"] = 23
operations["proposal_delete"] = 24
operations["withdraw_permission_create"] = 25
operations["withdraw_permission_update"] = 26
operations["withdraw_permission_claim"] = 27
operations["withdraw_permission_delete"] = 28
operations["committee_member_create"] = 29
operations["committee_member_update"] = 30
operations["committee_member_update_global_parameters"] = 31
operations["vesting_balance_create"] = 32
operations["vesting_balance_withdraw"] = 33
operations["worker_create"] = 34
operations["custom"] = 35
operations["assert"] = 36
operations["balance_claim"] = 37
operations["override_transfer"] = 38
operations["transfer_to_blind"] = 39
operations["blind_transfer"] = 40
operations["transfer_from_blind"] = 41
operations["asset_settle_cancel"] = 42
operations["asset_claim_fees"] = 43

chainid        = "ff3444b85c2185e1e53dcaa2bba7a898d8730a1a3bb6827d3718c24e6c45e51f"
prefix         = "BTS"

def getOperationNameForId(i):
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    return "Unknown Operation ID %d" % i

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

def JsonObj(data):
    return json.loads(str(data))

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
    def __init__(self)    : pass
    def __bytes__(self)   : return b''
    def __str__(self)     : return ""
class Array():
    def __init__(self,d)  : self.data = d; self.length = Varint32(len(self.data))
    def __bytes__(self)   : return bytes(self.length) + b"".join([bytes(a) for a in self.data])
    def __str__(self)     : return json.dumps([JsonObj(a) for a in self.data])
class PointInTime():
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return struct.pack("<I",timegm(time.strptime((self.data+"UTC"), '%Y-%m-%dT%H:%M:%S%Z')))
    def __str__(self)     : return self.data
class Signature():
    def __init__(self,d)  : self.data = d
    def __bytes__(self)   : return self.data
    def __str__(self)     : return json.dumps(hexlify(self.data).decode('ascii'))
class Bool(Uint8):
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
    def __bytes__(self)   : return bytes(Bool(1)) + bytes(self.data) if bytes(self.data) else bytes(Bool(0))
    def __str__(self)     : return str(self.data)
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

class Operation() :
    def __init__(self, op) :
        self.op = op
        self.name = type(self.op).__name__.lower()
        self.opId = operations[self.name]
    def __bytes__(self)   :
        return bytes(Id(self.opId)) + bytes(self.op)
    def __str__(self)     :  
        return json.dumps([self.opId, JsonObj(self.op)])

# Graphene objects
from collections import OrderedDict
class GrapheneObject(object) :
    def __init__(self, data=None):
        self.data = data 
    def __bytes__(self):
        if self.data == None : return bytes()
        b = b""
        for name, value in self.data.items():
            if isinstance(value, str) :
                b += bytes(value,'utf-8')
            else :
                b += bytes(value)
        return b
    def __json__(self) :
        if self.data == None : return {}
        d = {} ## JSON output is *not* ordered
        for name, value in self.data.items():
            try : 
                d.update( { name : JsonObj(value) } )
            except :
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
    def __init__(self, _from=None, _to=None, _nonce=None, _message=None):
        print(_message)
        if _message : 
            super().__init__(OrderedDict([
                           ('from',    PublicKey(_from, prefix=prefix)),
                           ('to',      PublicKey(_to, prefix=prefix)),
                           ('nonce',   Uint64(_nonce)),
                           ('message', Bytes(_message))
                         ]))
        else : 
            super().__init__(None)

class Signed_Transaction(GrapheneObject) :
    def __init__(self, refNum, refPrefix, expiration, operations):
        super().__init__(OrderedDict([
                      ('ref_block_num', Uint16(refNum)),
                      ('ref_block_prefix', Uint32(refPrefix)),
                      ('expiration', PointInTime(expiration)),
                      ('operations', Array(operations)),
                      ('signatures', Void()),
                    ]))

    def derSigToHexSig(self, s):
        s, junk = ecdsa.der.remove_sequence(unhexlify(s))
        if junk :
            print('JUNK: %s', hexlify(junk).decode('ascii'))
        assert(junk == b'')
        x, s = ecdsa.der.remove_integer(s)
        y, s = ecdsa.der.remove_integer(s)
        return '%064x%064x' % (x, y)

    def recoverPubkeyParameter(self, digest, signature, pubkey) :
        for i in range(0,4) :
            p = self.signature_to_public_key(digest, signature, i)
            if p.to_string() == pubkey.to_string() :
                return i
        return None

    def signature_to_public_key(self, digest, signature, i):
        # See http://www.secg.org/download/aid-780/sec1-v2.pdf section 4.1.6 primarily
        curve = ecdsa.SECP256k1.curve
        G     = ecdsa.SECP256k1.generator
        order = ecdsa.SECP256k1.order
        isYOdd      = i % 2
        isSecondKey = i // 2
        yp = 0 if (isYOdd) == 0 else 1
        r, s = ecdsa.util.sigdecode_string(signature, order)
        # 1.1
        x = r + isSecondKey * order
        # 1.3. This actually calculates for either effectively 02||X or 03||X depending on 'k' instead of always for 02||X as specified.
        # This substitutes for the lack of reversing R later on. -R actually is defined to be just flipping the y-coordinate in the elliptic curve.
        alpha = ((x * x * x) + (curve.a() * x) + curve.b()) % curve.p()
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, curve.p())
        if (beta - yp) % 2 == 0 :
            y = beta
        else :
            y = curve.p() - beta
        # 1.4 Constructor of Point is supposed to check if nR is at infinity. 
        R = ecdsa.ellipticcurve.Point(curve, x, y, order)
        # 1.5 Compute e
        e = ecdsa.util.string_to_number(digest)
        # 1.6 Compute Q = r^-1(sR - eG)
        Q = ecdsa.numbertheory.inverse_mod(r, order) * (s * R + (-e % order) * G)
        # Not strictly necessary, but let's verify the message for paranoia's sake.
        if ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1).verify_digest(signature, digest, sigdecode=ecdsa.util.sigdecode_string) != True:
            return None
        return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)

    def sign(self, wifkeys) :
        self.privkeys = []
        [self.privkeys.append(item) for item in wifkeys if item not in self.privkeys] # Unique private keys
        self.chainid  = chainid
        self.message  = unhexlify(chainid) + bytes(self)
        self.digest   = hashlib.sha256(self.message).digest()
        sigs = []
        for wif in self.privkeys :
            p     = bytes(PrivateKey(wif))
            sk    = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
            cnt   = 0
            while 1 :
                cnt += 1
                assert cnt<10, "Something wired happend while signing the transaction"
                ## Sign message
                k         = ecdsa.rfc6979.generate_k(sk.curve.generator.order(), sk.privkey.secret_multiplier, hashlib.sha256, self.digest+bytes(cnt))
                sigder    = sk.sign_digest(self.digest, sigencode=ecdsa.util.sigencode_der, k=k)
                hexSig    = self.derSigToHexSig(hexlify(sigder))  # DER decode
                signature = unhexlify(hexSig)
                ## Recovery parameter
                r, s      = ecdsa.util.sigdecode_string(signature, ecdsa.SECP256k1.order)
                if ecdsa.curves.orderlen( r ) is 32 or ecdsa.curves.orderlen( s ) is 32 : ## Verify length or r and s
                    i = self.recoverPubkeyParameter(self.digest, signature, sk.get_verifying_key())
                    i += 4  # compressed
                    i += 27 # compact
                    break
            sigstr = struct.pack("<B",i)
            sigstr += signature
            sigs.append( Signature(sigstr) )

        self.data["signature"] = Array(sigs)
        return self

class Transfer(GrapheneObject) :
    def __init__(self, _feeObj, _from, _to, _amountObj, _memo=None):
        super().__init__(OrderedDict([
                      ('fee'       , _feeObj),
                      ('from'      , Protocol_id_type("account",_from)),
                      ('to'        , Protocol_id_type("account",_to)),
                      ('amount'    , _amountObj),
                      ('memo'      , Optional(_memo))
                    ]))


if __name__ == '__main__':
    fee      = Asset(10, 15)
    amount   = Asset(1000000, 15)
    memo     = Memo("BTS774RSm2rJuktBbv9BUh7hj7WHsSXjviW16yy21qmtp7YAzK87L", "BTS774RSm2rJuktBbv9BUh7hj7WHsSXjviW16yy21qmtp7YAzK87L", 1244, "Foobar")
    transfer = Transfer(fee, 8, 10, amount, memo)

    print(json.dumps(json.loads(str(transfer)),indent=4))
    print(hexlify(bytes(transfer)))
