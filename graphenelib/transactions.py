import time
from calendar import timegm
from datetime import datetime
import json
import struct
from binascii import hexlify, unhexlify
import hashlib
import math
import ecdsa
import sys
from pprint import pprint
import time
from copy import copy

#import graphenelib.address as address
#from graphenelib.base58 import base58decode,base58encode,base58CheckEncode,base58CheckDecode,btsBase58CheckEncode,btsBase58CheckDecode

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

object_type = {}
object_type["null"] = 0
object_type["base"] = 1
object_type["key"] = 2
object_type["account"] = 3
object_type["asset"] = 4
object_type["force_settlement"] = 5
object_type["delegate"] = 6
object_type["witness"] = 7
object_type["limit_order"] = 8
object_type["short_order"] = 9
object_type["call_order"] = 10
object_type["custom"] = 11
object_type["proposal"] = 12
object_type["operation_history"] = 13
object_type["withdraw_permission"] = 14
object_type["bond_offer"] = 15
object_type["bond"] = 16
object_type["file"] = 17
object_type["OBJECT_TYPE_COUNT"] = 18

operations = {}
operations["transfer"] = 0
operations["limit_order_create"] = 1
operations["short_order_create"] = 2
operations["limit_order_cancel"] = 3
operations["short_order_cancel"] = 4
operations["call_order_update"] = 5
operations["key_create"] = 6
operations["account_create"] = 7
operations["account_update"] = 8
operations["account_whitelist"] = 9
operations["account_transfer"] = 10
operations["asset_create"] = 11
operations["asset_update"] = 12
operations["asset_update_bitasset"] = 13
operations["asset_update_feed_producers"] = 14
operations["asset_issue"] = 15
operations["asset_burn"] = 16
operations["asset_fund_fee_pool"] = 17
operations["asset_settle"] = 18
operations["asset_global_settle"] = 19
operations["asset_publish_feed"] = 20
operations["delegate_create"] = 21
operations["witness_create"] = 22
operations["witness_withdraw_pay"] = 23
operations["proposal_create"] = 24
operations["proposal_update"] = 25
operations["proposal_delete"] = 26
operations["withdraw_permission_create"] = 27
operations["withdraw_permission_update"] = 28
operations["withdraw_permission_claim"] = 29
operations["withdraw_permission_delete"] = 30
operations["fill_order"] = 31
operations["global_parameters_update"] = 32
operations["file_write"] = 33
operations["vesting_balance_create"] = 34
operations["vesting_balance_withdraw"] = 35
operations["bond_create_offer"] = 36
operations["bond_cancel_offer"] = 37
operations["bond_accept_offer"] = 38
operations["bond_claim_collateral"] = 39
operations["worker_create"] = 40
operations["custom"] = 41

reserved_spaces = {}
reserved_spaces["relative_protocol_ids"] = 0
reserved_spaces["protocol_ids"] = 1
reserved_spaces["implementation_ids"] = 2
reserved_spaces["RESERVE_SPACES_COUNT"] = 3

chainid        = "75c11a81b7670bbaa721cc603eadb2313756f94a3bcbb9928e9101432701ac5f"
PREFIX         = "BTS"


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

"""
Variable types
"""
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

"""
Protocol wire format
"""

class Protocol_id_type() :
    def __init__(self, _type, _object):
        self.id_type   = _type
        self.data      = Id(_object)
    def __bytes__(self):
        return bytes(self.data)
    def __str__(self) :
        d = {}
        d[ self.id_type ] = str(self.data)
        return json.dumps(d)

class Asset() :
    def __init__(self, _amount, _asset):
        self.amount   = Uint64(_amount)
        self.asset_id = _asset
    def __bytes__(self):
        return bytes(self.amount) + bytes(self.asset_id)
    def __str__(self) :
        d             = {}
        d["amount"]   = str(self.amount)
        d["asset_id"] = JsonObj(self.asset_id)
        return json.dumps(d)

class Memo() :
    def __init__(self, _from, _to, _nonce, _message) :
        self._from   = _from
        self.to      = _to
        self.nonce   = Uint64(_nonce)
        self.message = _message
    def __bytes__(self):
        return (bytes(self._from)            +
                bytes(self.to)               +
                bytes(self.nonce) +
                self.message.encode('utf-8'))
    def __str__(self) :
        d            = {}
        d["from"]    = JsonObj(self._from)
        d["to"]      = JsonObj(self.to)
        d["nonce"]   = str(self.nonce)
        d["message"] = self.message
        return json.dumps(d)

class Transfer() :
    def __init__(self, _fee, _from, _to, _amount, _memo) :
        self.fee     = _fee
        self._from   = _from
        self.to      = _to
        self.amount  = _amount
        self.memo    = _memo
    def __bytes__(self):
        return (bytes(self.fee)   +
                bytes(self._from) +
                bytes(self.to)    +
                bytes(self.amount)+
                bytes(self.memo))
    def __str__(self) :
        d           = {}
        d["fee"]    = JsonObj(self.fee)
        d["from"]   = JsonObj(self._from)
        d["to"]     = JsonObj(self.to)
        d["amount"] = JsonObj(self.amount)
        d["memo"]   = JsonObj(self.memo)
        return json.dumps(d)

asset_id = Protocol_id_type("asset", 8)
fee    = Asset(10, asset_id)
amount = Asset(1000000, asset_id)
_from = Protocol_id_type("key", 8)
to    = Protocol_id_type("key", 10)
memo  = Memo(_from,to,1244,"Foobar")
transfer = Transfer(fee, _from, to, amount, memo)
print(hexlify(bytes(transfer)))
print(b'0a0000000000000008080a40420f000000000008080adc04000000000000466f6f626172')
print(json.dumps(json.loads(str(transfer)),indent=4))












# class Memo(object) :
#     def __init__(self,otk,data) :
#         self.one_time_key        = otk
#         self.encrypted_memo_data = data
#         raise Exception( "Memo not working currently" )
#     def towire(self) :
#         wire  = struct.pack("<33s",btsBase58CheckDecode(self.one_time_key[len(PREFIX):]))
#         wire += variable_buffer( self.encrypted_memo_data )
#         return wire
#     def tojson(self) :
#         return vars(self)
# 
# class WithdrawSignatureType(object) :
#     def __init__(self, receiveAddress, memo=None) :
#         self.owner = receiveAddress
#         self.memo = None #memo
#     def towire(self) :
#         wire  = struct.pack("<20s",btsBase58CheckDecode(self.owner[len(PREFIX):]))
#         if self.memo :
#             wire += struct.pack("<B", 0x01)
#             wire += self.memo.towire()
#         else :
#             wire += struct.pack("<B", 0x00)
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         if self.memo :
#             d["memo"] = self.memo.tojson()
#         return d
#     @staticmethod
#     def fromjson(j) :
#         return WithdrawSignatureType(j["owner"], j["memo"])
# 
# class WithdrawCondition(object) :
#     def encodeZigZag32(self,n): return (n << 1) ^ (n >> 31)
#     def encodeZigZag64(self,n): return (n << 1) ^ (n >> 63)
#     def decodeZigZag32(self,n): return (n >> 1) ^ -(n & 1)
#     def decodeZigZag64(self,n): return (n >> 1) ^ -(n & 1)
# 
#     def __init__( self, asset_id, slate_id, condition_type, condition ) :
#         self.asset_id = asset_id
#         self.slate_id = slate_id
#         self.type = condition_type
#         self.data = condition
#     def towire(self) :
#         wire  = varint(self.encodeZigZag32(self.asset_id))
#         wire += struct.pack("<Q",int(self.slate_id) if self.slate_id else 0) 
#         wire += struct.pack("<B",bts_withdraw[self.type]) 
#         wire += variable_buffer(self.data.towire())
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         d["data"] = self.data.tojson()
#         return d
#     @staticmethod
#     def fromjson(j) :
#         if j["type"] == "withdraw_signature_type" :
#             condition = WithdrawSignatureType.fromjson(j["data"])
#         else : raise("Not implemented")
#         return WithdrawCondition(j["asset_id"], j["slate_id"], j["type"], condition)
# 
# class Deposit(object) :
#     def __init__( self, amount, condition ) :
#         self.amount = int(amount)
#         self.condition = condition
#     def towire(self) :
#         wire = struct.pack("<Q",self.amount)
#         wire += self.condition.towire()
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         d["amount"] = str(self.amount)
#         d["condition"] = self.condition.tojson()
#         return d
#     @staticmethod
#     def fromjson(j) :
#         condition = WithdrawCondition.fromjson(j["condition"])
#         return Deposit( j["amount"], condition )
# 
# class Withdraw(object) :
#     def __init__( self, balance_id, amount, claimdata="") :
#         self.balance_id = balance_id
#         self.amount = int(amount)
#         self.claim_input_data = claimdata
#     def towire(self) :
#         wire  = struct.pack("<20s",btsBase58CheckDecode(self.balance_id[len(PREFIX):]))
#         wire += struct.pack("<Q",self.amount)
#         wire += variable_buffer(self.claim_input_data)
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         d["amount"] = str(self.amount)
#         return d
#     @staticmethod
#     def fromjson(j) :
#         return Withdraw(j["balance_id"], int(j["amount"]), j["claim_input_data"])
# 
# class UpdateBalanceVote(object) :
#     def __init__( self, balance_id, vote_address, slate_id) :
#         self.balance_id = balance_id
#         self.new_restricted_owner = vote_address
#         self.new_slate = slate_id
#     def towire(self) :
#         wire  = struct.pack("<20s",btsBase58CheckDecode(self.balance_id[len(PREFIX):]))
#         wire += struct.pack("<B", 0x01) # optional
#         wire += struct.pack("<20s",btsBase58CheckDecode(self.new_restricted_owner[len(PREFIX):]))
#         wire += struct.pack("<Q",int(self.new_slate) if self.new_slate else 0)
#         return wire
#     def tojson(self) :
#         return vars(self)
#     @staticmethod
#     def fromjson(j) :
#         return UpdateBalanceVote(j["balance_id"],j["new_restricted_owner"],j["new_slate"])
# 
# class Operation(object) :
#     def __init__( self, optype, operation ) :
#         self.type = optype
#         self.data = operation
#     def towire(self) :
#         wire  = struct.pack("<B",bts_operations[self.type])
#         wire += variable_buffer(self.data.towire())
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         d["data"] = self.data.tojson()
#         return d
#     @staticmethod
#     def fromjson(j) :
#         if   j["type"] == "deposit_op_type" :
#             operation = Deposit.fromjson(j["data"])
#         elif j["type"] == "withdraw_op_type" :
#             operation = Withdraw.fromjson(j["data"])
#         elif j["type"] == "update_balance_vote_op_type" :
#             operation = UpdateBalanceVote.fromjson(j["data"])
#         else : raise("not implemented")
#         return Operation(j["type"], operation)
# 
# class Transaction(object) :
#     def __init__( self, timeoutsecs, slate_id, operations ) :
#         self.expiration = int(time.time()) + timeoutsecs
#         self.slate_id = None # FIXME slate_id
#         self.operations = operations
#     def towire(self) :
#         wire  = struct.pack("<I",self.expiration )
#         wire += struct.pack("<B",int(self.slate_id) if self.slate_id else 0)
#         wire += varint(len(self.operations))
#         for op in self.operations :
#             wire += op.towire()
#         return wire
#     def tojson(self) :
#         d = vars(copy(self))
#         d["expiration"] = datetime.utcfromtimestamp(int(d["expiration"])).strftime('%Y-%m-%dT%H:%M:%S')
#         d["operations"] = []
#         for op in self.operations :
#             d["operations"].append(op.tojson())
#         return d
#     @staticmethod
#     def fromjson(j) :
#         oplist = []
#         for op in j["operations"] :
#             oplist.append(Operation.fromjson(op))
#         expiration = timegm(time.strptime((j["expiration"]+"UTC"), '%Y-%m-%dT%H:%M:%S%Z'))
#         return Transaction(expiration-int(time.time()), j["slate_id"], oplist )
# 
# class SignedTransaction(object) : 
#     def derSigToHexSig(self, s):
#         s, junk = ecdsa.der.remove_sequence(s.decode('hex'))
#         if junk != '':
#             print('JUNK', junk.encode('hex'))
#         assert(junk == '')
#         x, s = ecdsa.der.remove_integer(s)
#         y, s = ecdsa.der.remove_integer(s)
#         return '%064x%064x' % (x, y)
# 
#     def recoverPubkeyParameter(self, digest, signature, pubkey) :
#         for i in xrange(0,4) :
#             p = self.signature_to_public_key(digest, signature, i)
#             if p.to_string() == pubkey.to_string() :
#                 return i
#         return None
# 
#     def signature_to_public_key(self, digest, signature, i):
#         # See http://www.secg.org/download/aid-780/sec1-v2.pdf section 4.1.6 primarily
#         curve = ecdsa.SECP256k1.curve
#         G     = ecdsa.SECP256k1.generator
#         order = ecdsa.SECP256k1.order
#         isYOdd      = i % 2
#         isSecondKey = i // 2
#         yp = 0 if (isYOdd) == 0 else 1
#         r, s = ecdsa.util.sigdecode_string(signature, order)
#         # 1.1
#         x = r + isSecondKey * order
#         # 1.3. This actually calculates for either effectively 02||X or 03||X depending on 'k' instead of always for 02||X as specified.
#         # This substitutes for the lack of reversing R later on. -R actually is defined to be just flipping the y-coordinate in the elliptic curve.
#         alpha = ((x * x * x) + (curve.a() * x) + curve.b()) % curve.p()
#         beta = ecdsa.numbertheory.square_root_mod_prime(alpha, curve.p())
#         if (beta - yp) % 2 == 0 :
#             y = beta
#         else :
#             y = curve.p() - beta
#         # 1.4 Constructor of Point is supposed to check if nR is at infinity. 
#         R = ecdsa.ellipticcurve.Point(curve, x, y, order)
#         # 1.5 Compute e
#         e = ecdsa.util.string_to_number(digest)
#         # 1.6 Compute Q = r^-1(sR - eG)
#         Q = ecdsa.numbertheory.inverse_mod(r, order) * (s * R + (-e % order) * G)
#         # Not strictly necessary, but let's verify the message for paranoia's sake.
#         if ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1).verify_digest(signature, digest, sigdecode=ecdsa.util.sigdecode_string) != True:
#             return None
#         return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)
# 
#     def __init__( self, transaction, privatekeys ) :
#         self.transaction = transaction
#         self.privkeys = []
#         [self.privkeys.append(item) for item in privatekeys if item not in self.privkeys] # Unique private keys
#         self.chainid  = chainid
#         self.message  = transaction.towire() + binascii.unhexlify(chainid)
#         self.digest   = hashlib.sha256(self.message).digest()
#         self.signatures = self.signtx()
# 
#     def signtx(self) :
#         sigs = []
#         for wif in self.privkeys :
#             p     = address.wif2bin(wif)
#             sk    = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
#             cnt   = 0
#             while 1 :
#                 cnt += 1
#                 assert cnt<10, "Something wired happend while signing the transaction"
#                 ## Sign message
#                 k         = ecdsa.rfc6979.generate_k(sk.curve.generator.order(), sk.privkey.secret_multiplier, hashlib.sha256, self.digest+str(cnt))
#                 sigder    = sk.sign_digest(self.digest, sigencode=ecdsa.util.sigencode_der, k=k)
#                 hexSig    = self.derSigToHexSig(binascii.hexlify(sigder))  # DER decode
#                 signature = binascii.unhexlify(hexSig)
#                 ## Recovery parameter
#                 r, s      = ecdsa.util.sigdecode_string(signature, ecdsa.SECP256k1.order)
#                 if ecdsa.curves.orderlen( r ) is 32 or ecdsa.curves.orderlen( s ) is 32 : ## Verify length or r and s
#                     i = self.recoverPubkeyParameter(self.digest, signature, sk.get_verifying_key())
#                     i += 4  # compressed
#                     i += 27 # compact
#                     break
#             sigstr = struct.pack("<B",i)
#             sigstr += signature
#             sigs.append( sigstr )
#         return sigs
# 
#     def towire(self) :
#         wire = self.transaction.towire()
#         wire += varint(len(self.signatures))
#         for s in self.signatures :
#             wire += s
#         return wire
# 
#     def tojson(self) :
#         d = self.transaction.tojson()
#         d["signatures"] = []
#         for s in self.signatures :
#             d["signatures"].append(binascii.hexlify(s))
#         return d
# 
# def test_constructdeposit():
#     receiveAddress = "BTSHuF9nZoHjD7i9pgL1UJbMG3dGZYEDza8"
#     balance_id     = "BTSMnJT3Vy3MMSgjk5tfM7aCfQfgeTGpckcQ"
#     privKey        = "5Jn9G5pDMwJMPbAkEiTFFrjVrgpoPE6mE5PpUHfJoZwGVkYvQNg"
#     otk            = None
#     asset_id       = 0      # BTS
#     amount         = 1*1e5 - fee
#     withdraw       = Withdraw(balance_id, amount+fee)
#     wst            = WithdrawSignatureType( receiveAddress )
#     wc             = WithdrawCondition( asset_id, "0", "withdraw_signature_type", wst)
#     deposit        = Deposit( amount, wc )
#     ops = []
#     ops.append(Operation( "deposit_op_type", deposit))
#     ops.append(Operation( "withdraw_op_type", withdraw ))
#     tx             = Transaction( 60*60*12, None, ops )
#     sigtx          = SignedTransaction(tx, [privKey])
#     return sigtx
# 
# def test_constructvotekey() :
#     balance_id     = "BTSMnJT3Vy3MMSgjk5tfM7aCfQfgeTGpckcQ"
#     privKey        = "5Jn9G5pDMwJMPbAkEiTFFrjVrgpoPE6mE5PpUHfJoZwGVkYvQNg"
#     newvoteaddress = "BTSHuF9nZoHjD7i9pgL1UJbMG3dGZYEDza8"
#     votekeyop      = UpdateBalanceVote(balance_id, newvoteaddress, slate_id)
#     ops            = []
#     ops.append(Operation( "update_balance_vote_op_type", votekeyop ))
#     tx             = Transaction( 60*60*12, None, ops )
#     sigtx          = SignedTransaction(tx, [privKey])
#     return sigtx
# 
# if __name__ == '__main__':
#     #import graphenerpc
#     #rpc = graphenerpc.client("http://127.0.0.1:19988/rpc", "", "")
#     fee            = .1 * 1e5
#     slate_id       = None   # no slate
# 
#     #sigtx = test_constructdeposit()
#     sigtx = test_constructvotekey()
# 
#     #pprint( sigtx.tojson() )
#     #x = Transaction.fromjson((sigtx.tojson()))
#     #pprint( x.tojson() )
# 
#     print( "= Wire Format" )
#     print( binascii.hexlify(sigtx.towire()) )
#     print( "= JSON Format" )
#     print(json.dumps(sigtx.tojson(),indent=4))
#     print( "= Paste Format" )
#     print( "blockchain_broadcast_transaction "+json.dumps(sigtx.tojson()).replace(' ','') )
#     #print rpc.blockchain_broadcast_transaction(sigtx.tojson())
