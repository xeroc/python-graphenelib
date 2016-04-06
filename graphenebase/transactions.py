from collections import OrderedDict
from binascii import hexlify, unhexlify
from calendar import timegm
from datetime import datetime
import ecdsa
import hashlib
import json
import struct
import time
from graphenebase.account import PrivateKey, PublicKey

timeformat = '%Y-%m-%dT%H:%M:%S%Z'

#: Reserved spaces for object ids
reserved_spaces = {}
reserved_spaces["relative_protocol_ids"] = 0
reserved_spaces["protocol_ids"] = 1
reserved_spaces["implementation_ids"] = 2

#: Object types for object ids
object_type = {}
object_type["null"] = 0
object_type["base"] = 1
object_type["account"] = 2
object_type["asset"] = 3
object_type["force_settlement"] = 4
object_type["committee_member"] = 5
object_type["witness"] = 6
object_type["limit_order"] = 7
object_type["call_order"] = 8
object_type["custom"] = 9
object_type["proposal"] = 10
object_type["operation_history"] = 11
object_type["withdraw_permission"] = 12
object_type["vesting_balance"] = 13
object_type["worker"] = 14
object_type["balance"] = 15
object_type["OBJECT_TYPE_COUNT"] = 16

#: Operation ids
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

# : Vote types
vote_type = {}
vote_type["committee"] = 0
vote_type["witness"] = 1
vote_type["worker"] = 2

# : Networks
known_chains = {"BTS" : {"chain_id" : "4018d7844c78f6a6c41c6a552b898022310fc5dec06da467ee7905a8dad512c8",
                         "core_symbol" : "BTS",
                         "prefix" : "BTS"},
                "GPH" : {"chain_id" : "b8d1603965b3eb1acba27e62ff59f74efa3154d43a4188d381088ac7cdf35539",
                         "core_symbol" : "CORE",
                         "prefix" : "GPH"},
                }


def getOperationNameForId(i) :
    """ Convert an operation id into the corresponding string
    """
    for key in operations :
        if int(operations[key]) is int(i) :
            return key
    return "Unknown Operation ID %d" % i


def varint(n) :
    """ Varint encoding
    """
    data = b''
    while n >= 0x80 :
        data += bytes([(n & 0x7f) | 0x80])
        n >>= 7
    data += bytes([n])
    return data


def varintdecode(data) :
    """ Varint decoding
    """
    shift = 0
    result = 0
    for c in data :
        b = ord(c)
        result |= ((b & 0x7f) << shift)
        if not (b & 0x80) :
            break
        shift += 7
    return result


def variable_buffer(s) :
    """ Encode variable length bugger
    """
    return varint(len(s)) + s


def JsonObj(data) :
    """ Returns json object from data
    """
    return json.loads(str(data))


class Uint8() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<B", self.data)

    def __str__(self) :
        return '%d' % self.data


class Uint16() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<H", self.data)

    def __str__(self) :
        return '%d' % self.data


class Uint32() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<I", self.data)

    def __str__(self) :
        return '%d' % self.data


class Uint64() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<Q", self.data)

    def __str__(self) :
        return '%d' % self.data


class Varint32() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return varint(self.data)

    def __str__(self) :
        return '%d' % self.data


class Int64() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<q", self.data)

    def __str__(self) :
        return '%d' % self.data


class String() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return varint(len(self.data)) + bytes(self.data, 'utf-8')

    def __str__(self) :
        return '%d' % str(self.data)


class Bytes() :
    def __init__(self, d, length=None) :
        self.data = d
        if length :
            self.length = length
        else :
            self.length = len(self.data)

    def __bytes__(self) :
        d = unhexlify(bytes(self.data, 'utf-8'))
        return varint(len(d)) + d

    def __str__(self) :
        return str(self.data)


class Void() :
    def __init__(self) :
        pass

    def __bytes__(self) :
        return b''

    def __str__(self) :
        return ""


class Array() :
    def __init__(self, d) :
        self.data = d
        self.length = Varint32(len(self.data))

    def __bytes__(self) :
        return bytes(self.length) + b"".join([bytes(a) for a in self.data])

    def __str__(self) :
        return json.dumps([JsonObj(a) for a in self.data])


class PointInTime() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return struct.pack("<I", timegm(time.strptime((self.data + "UTC"), timeformat)))

    def __str__(self) :
        return self.data


class Signature() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return self.data

    def __str__(self) :
        return json.dumps(hexlify(self.data).decode('ascii'))


class Bool(Uint8) :  # Bool = Uint8
    def __init__(self, d) :
        super().__init__(d)


class Set(Array) :  # Set = Array
    def __init__(self, d) :
        super().__init__(d)


class Fixed_array() :
    def __init__(self, d) :
        raise NotImplementedError

    def __bytes__(self) :
        raise NotImplementedError

    def __str__(self) :
        raise NotImplementedError


class Optional() :
    def __init__(self, d) :
        self.data = d

    def __bytes__(self) :
        return bytes(Bool(1)) + bytes(self.data) if bytes(self.data) else bytes(Bool(0))

    def __str__(self) :
        return str(self.data)

    def isempty(self) :
        return not bool(bytes(self.data))


class Static_variant() :
    def __init__(self, d, type_id) :
        self.data = d
        self.type_id = type_id

    def __bytes__(self) :
        return varint(self.type_id) + bytes(self.data)

    def __str__(self) :
        return {self._type_id : str(self.data)}


class Map() :
    def __init__(self, d) :
        raise NotImplementedError

    def __bytes__(self) :
        raise NotImplementedError

    def __str__(self) :
        raise NotImplementedError


class Id() :
    def __init__(self, d) :
        self.data = Varint32(d)

    def __bytes__(self) :
        return bytes(self.data)

    def __str__(self) :
        return str(self.data)


class Operation() :
    def __init__(self, op) :
        self.op = op
        self.name = type(self.op).__name__.lower()  # also store name
        self.opId = operations[self.name]

    def __bytes__(self) :
        return bytes(Id(self.opId)) + bytes(self.op)

    def __str__(self) :
        return json.dumps([self.opId, JsonObj(self.op)])


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
            try :
                d.update({name : JsonObj(value)})
            except :
                d.update({name : str(value)})
        return OrderedDict(d)

    def __str__(self) :
        return json.dumps(self.__json__())


class ObjectId() :
    """ Encodes object/protocol ids
    """
    def __init__(self, object_str, type_verify=None) :
        if len(object_str.split(".")) == 3 :
            space, type, id = object_str.split(".")
            self.space = int(space)
            self.type = int(type)
            self.instance = Id(int(id))
            self.Id = object_str
            if type_verify :
                assert object_type[type_verify] == int(type), "Object id does not match object type!"
        else :
            raise Exception("Object id is invalid")

    def __bytes__(self) :
        return bytes(self.instance)  # only yield instance

    def __str__(self) :
        return self.Id


class Signed_Transaction(GrapheneObject) :
    """ Create a signed transaction and offer method to create the
        signature

        :param num refNum: parameter ref_block_num (see ``getBlockParams``)
        :param num refPrefix: parameter ref_block_prefix (see ``getBlockParams``)
        :param str expiration: expiration date
        :param Array operations:  array of operations
    """
    def __init__(self, refNum, refPrefix, expiration, operations) :
        super().__init__(OrderedDict([
            ('ref_block_num', Uint16(refNum)),
            ('ref_block_prefix', Uint32(refPrefix)),
            ('expiration', PointInTime(expiration)),
            ('operations', Array(operations)),
            ('extensions', Set([])),
            ('signatures', Void()),
        ]))

    def recoverPubkeyParameter(self, digest, signature, pubkey) :
        """ Use to derive a number that allows to easily recover the
            public key from the signature
        """
        for i in range(0, 4) :
            p = self.recover_public_key(digest, signature, i)
            if p.to_string() == pubkey.to_string() :
                return i
        return None

    def derSigToHexSig(self, s) :
        """ Format DER to HEX signature
        """
        s, junk = ecdsa.der.remove_sequence(unhexlify(s))
        if junk :
            print('JUNK : %s', hexlify(junk).decode('ascii'))
        assert(junk == b'')
        x, s = ecdsa.der.remove_integer(s)
        y, s = ecdsa.der.remove_integer(s)
        return '%064x%064x' % (x, y)

    def recover_public_key(self, digest, signature, i) :
        """ Recover the public key from the the signature
        """
        # See http : //www.secg.org/download/aid-780/sec1-v2.pdf section 4.1.6 primarily
        curve = ecdsa.SECP256k1.curve
        G = ecdsa.SECP256k1.generator
        order = ecdsa.SECP256k1.order
        isYOdd = i % 2
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
        if not ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1).verify_digest(signature, digest, sigdecode=ecdsa.util.sigdecode_string) :
            return None
        return ecdsa.VerifyingKey.from_public_point(Q, curve=ecdsa.SECP256k1)

    def sign(self, wifkeys, chain="BTS") :
        """ Sign the transaction with the provided private keys.

            :param array wifkeys: Array of wif keys
            :param str chain: identifier for the chain

        """
        # Which network are we on :
        if isinstance(chain, str) and chain in known_chains :
            chain_params = known_chains[chain]
        elif isinstance(chain, dict) :
            chain_params = chain
        else :
            raise Exception("sign() only takes a string or a dict as chain!")
        if "chain_id" not in chain_params :
            raise Exception("sign() needs a 'chain_id' in chain params!")

        # Get Unique private keys
        self.privkeys = []
        [self.privkeys.append(item) for item in wifkeys if item not in self.privkeys]

        # Chain ID
        self.chainid = chain_params["chain_id"]

        # Get message to sign
        #   bytes(self) will give the wire formated data according to
        #   GrapheneObject and the data given in __init__()
        self.message = unhexlify(self.chainid) + bytes(self)
        self.digest = hashlib.sha256(self.message).digest()

        # Sign the message with every private key given!
        sigs = []
        for wif in self.privkeys :
            p = bytes(PrivateKey(wif))
            sk = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
            cnt = 0
            i = 0
            while 1 :
                cnt += 1
                if not cnt % 20 :
                    print("Still searching for a canonical signature. Tried %d times already!" % cnt)

                # Deterministic k
                #
                k = ecdsa.rfc6979.generate_k(
                    sk.curve.generator.order(),
                    sk.privkey.secret_multiplier,
                    hashlib.sha256,
                    hashlib.sha256(self.digest + (b'%x' % cnt)).digest())

                # Sign message
                #
                sigder = sk.sign_digest(
                    self.digest,
                    sigencode=ecdsa.util.sigencode_der,
                    k=k)

                # Reformating of signature
                #
                r, s = ecdsa.util.sigdecode_der(sigder, sk.curve.generator.order())
                signature = ecdsa.util.sigencode_string(r, s, sk.curve.generator.order())

                # Make sure signature is canonical!
                #
                lenR = sigder[3]
                lenS = sigder[5 + lenR]
                if lenR is 32 and lenS is 32 :
                    # Derive the recovery parameter
                    #
                    i = self.recoverPubkeyParameter(self.digest, signature, sk.get_verifying_key())
                    i += 4   # compressed
                    i += 27  # compact
                    break

            # pack signature
            #
            sigstr = struct.pack("<B", i)
            sigstr += signature

            sigs.append(Signature(sigstr))

        self.data["signatures"] = Array(sigs)
        return self

"""##############################################################
         Auxiliary calls that require a websocket connection!
##############################################################"""


def addRequiredFees(ws, ops, asset_id) :
    """ Auxiliary method to obtain the required fees for a set of
        operations. Requires a websocket connection to a witness node!
    """
    fees = ws.get_required_fees([JsonObj(i) for i in ops], asset_id)
    for i, d in enumerate(ops) :
        ops[i].op.data["fee"] = Asset(
            amount=fees[i]["amount"],
            asset_id=fees[i]["asset_id"]
        )
    return ops


def getBlockParams(ws) :
    """ Auxiliary method to obtain ``ref_block_num`` and
        ``ref_block_prefix``. Requires a websocket connection to a
        witness node!
    """
    dynBCParams = ws.get_object("2.1.0")
    ref_block_num = dynBCParams["head_block_number"] & 0xFFFF
    ref_block_prefix = struct.unpack_from("<I", unhexlify(dynBCParams["head_block_id"]), 4)[0]
    return ref_block_num, ref_block_prefix

"""##############################################################
         Other auxiliary calls
##############################################################"""


def formatTimeFromNow(secs=0) :
    """ Properly Format Time that is `x` seconds in the future

     :param int secs: Seconds to go in the future (`x>0`) or the past (`x<0`)
     :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
     :rtype: str

    """
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime(timeformat)

"""##############################################################
         Actual Objects are coming below this line
##############################################################"""


class Asset(GrapheneObject) :
    """ Asset object

        usage:::

            fee = Asset(<amount>, <asset_id>)
            fee = Asset(10, "1.3.0")
    """
    def __init__(self, *args, **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            super().__init__(OrderedDict([
                ('amount',   Int64(kwargs["amount"])),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset"))
            ]))


class Memo(GrapheneObject) :
    """ Memo object

        usage:::

            encrypted_memo = memo.encode_memo(
                account.PrivateKey(Config.wif),
                account.PublicKey(to_account["options"]["memo_key"], prefix=Config.prefix),
                nonce,
                Config.message)
            memoObj = transactions.Memo(
                from_account["options"]["memo_key"],
                to_account["options"]["memo_key"],
                nonce, encrypted_memo,
                chain=self.connected_chain)
     """
    def __init__(self, *args, chain="BTS", **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            if "message" in kwargs and kwargs["message"] :
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
    """ Price Object.

        Usage:::

            quote = Asset(<amount>, <asset_id>)
            base  = Asset(<amount>, <asset_id>)
            price = Price(quote, base)
            

    """
    def __init__(self, *args, **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            super().__init__(OrderedDict([
                ('base', Asset(kwargs["base"])),
                ('quote', Asset(kwargs["quote"]))
            ]))


class PriceFeed(GrapheneObject):
    def __init__(self, *args, **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            super().__init__(OrderedDict([
                ('settlement_price', Price(kwargs["settlement_price"])),
                ('maintenance_collateral_ratio', Uint16(kwargs["maintenance_collateral_ratio"])),
                ('maximum_short_squeeze_ratio', Uint16(kwargs["maximum_short_squeeze_ratio"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
            ]))

"""
             O P E R A T I O N S
"""


class Transfer(GrapheneObject) :
    """ Transfer object

        usage:::

            transfer = transactions.Transfer(
                fee,
                from_account["id"],
                to_account["id"],
                amount,
                memoObj)
    """
    def __init__(self, *args, **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            super().__init__(OrderedDict([
                ('fee'       , Asset(kwargs["fee"])),
                ('from'      , ObjectId(kwargs["from"], "account")),
                ('to'        , ObjectId(kwargs["to"], "account")),
                ('amount'    , Asset(kwargs["amount"])),
                ('memo'      , Optional(Memo(kwargs["memo"]))),
                ('extensions', Set([])),
            ]))


class Asset_publish_feed(GrapheneObject):
    def __init__(self, *args, **kwargs) :
        if (len(args) == 1 and
            type(args[0]).__name__ == type(self).__name__):
            self.data = args[0].data
        else:
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('publisher', ObjectId(kwargs["publisher"], "account")),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset")),
                ('feed', PriceFeed(kwargs["feed"])),
                ('extensions', Set([])),
            ]))
