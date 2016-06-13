import ecdsa
import hashlib
from binascii import hexlify, unhexlify
import struct
from collections import OrderedDict

from .account import PrivateKey, PublicKey
from .types import (
    Array,
    Set,
    Signature,
    PointInTime,
    Uint16,
    Uint32,
)
from .objects import GrapheneObject, isArgsThisClass
from .operations import Operation
from .chains import known_chains


class Signed_Transaction(GrapheneObject) :
    """ Create a signed transaction and offer method to create the
        signature

        :param num refNum: parameter ref_block_num (see ``getBlockParams``)
        :param num refPrefix: parameter ref_block_prefix (see ``getBlockParams``)
        :param str expiration: expiration date
        :param Array operations:  array of operations
    """
    def __init__(self, *args, **kwargs) :
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "extensions" not in kwargs:
                kwargs["extensions"] = Set([])
            if "signatures" not in kwargs:
                kwargs["signatures"] = Array([])
            else:
                kwargs["signatures"] = Array([Signature(unhexlify(a)) for a in kwargs["signatures"]])

            if "operations" in kwargs:
                if all([not isinstance(a, Operation) for a in kwargs["operations"]]):
                    kwargs['operations'] = Array([Operation(a) for a in kwargs["operations"]])
                else:
                    kwargs['operations'] = Array(kwargs["operations"])

            super().__init__(OrderedDict([
                ('ref_block_num', Uint16(kwargs['ref_block_num'])),
                ('ref_block_prefix', Uint32(kwargs['ref_block_prefix'])),
                ('expiration', PointInTime(kwargs['expiration'])),
                ('operations', kwargs['operations']),
                ('extensions', kwargs['extensions']),
                ('signatures', kwargs['signatures']),
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
        yp = (i % 2)
        r, s = ecdsa.util.sigdecode_string(signature, order)
        # 1.1
        x = r + (i // 2) * order
        # 1.3. This actually calculates for either effectively 02||X or 03||X depending on 'k' instead of always for 02||X as specified.
        # This substitutes for the lack of reversing R later on. -R actually is defined to be just flipping the y-coordinate in the elliptic curve.
        alpha = ((x * x * x) + (curve.a() * x) + curve.b()) % curve.p()
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, curve.p())
        y = beta if (beta - yp) % 2 == 0 else curve.p() - beta
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

    def deriveDigest(self, chain):
        # Which network are we on :
        if isinstance(chain, str) and chain in known_chains :
            chain_params = known_chains[chain]
        elif isinstance(chain, dict) :
            chain_params = chain
        else :
            raise Exception("sign() only takes a string or a dict as chain!")
        if "chain_id" not in chain_params :
            raise Exception("sign() needs a 'chain_id' in chain params!")

        # Chain ID
        self.chainid = chain_params["chain_id"]

        # Do not serialize signatures
        sigs = self.data["signatures"]
        self.data["signatures"] = []

        # Get message to sign
        #   bytes(self) will give the wire formated data according to
        #   GrapheneObject and the data given in __init__()
        self.message = unhexlify(self.chainid) + bytes(self)
        self.digest = hashlib.sha256(self.message).digest()

        # restore signatures
        self.data["signatures"] = sigs

    def verify(self, pubkeys, chain):
        self.deriveDigest(chain)
        signatures = self.data["signatures"].data
        pubKeysFound = []

        for signature in signatures:
            sig = bytes(signature)[1:]
            recoverParameter = (bytes(signature)[0]) - 4 - 27  # recover parameter only
            p = self.recover_public_key(self.digest, sig, recoverParameter)
            # Will throw an exception of not valid
            p.verify_digest(
                sig,
                self.digest,
                sigdecode=ecdsa.util.sigdecode_string
            )
            phex = hexlify(p.to_string()).decode('ascii')
            pubKeysFound.append(phex)

        for pubkey in pubkeys:
            if not isinstance(pubkey, PublicKey):
                raise Exception("Pubkeys must be array of 'PublicKey'")

            k = pubkey.unCompressed()[2:]
            if k not in pubKeysFound:
                k = PublicKey(PublicKey(k).compressed())
                f = format(k, chain)
                raise Exception("Signature for %s missing!" % f)

        return True

    def sign(self, wifkeys, chain="STEEM") :
        """ Sign the transaction with the provided private keys.

            :param array wifkeys: Array of wif keys
            :param str chain: identifier for the chain

        """
        self.deriveDigest(chain)

        # Get Unique private keys
        self.privkeys = []
        [self.privkeys.append(item) for item in wifkeys if item not in self.privkeys]

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
