# -*- coding: utf-8 -*-
from __future__ import absolute_import
import hashlib
import logging

# We load 'ecdsa' from installation and .ecdsa from relative
# import ecdsa
from .ecdsa import sign_message, verify_message

from binascii import hexlify, unhexlify
from collections import OrderedDict
from .account import PublicKey
from .types import Array, Set, Signature, PointInTime, Uint16, Uint32
from .objects import GrapheneObject, Operation
from .chains import known_chains

log = logging.getLogger(__name__)

try:
    import secp256k1

    USE_SECP256K1 = True
    log.debug("Loaded secp256k1 binding.")
except ImportError:
    USE_SECP256K1 = False
    log.debug("To speed up transactions signing install \n" "    pip install secp256k1")


class MissingSignatureForKey(Exception):
    pass


class Signed_Transaction(GrapheneObject):
    """ Create a signed transaction and offer method to create the
        signature

        :param num refNum: parameter ref_block_num (see ``getBlockParams``)
        :param num refPrefix: parameter ref_block_prefix (see
            ``getBlockParams``)
        :param str expiration: expiration date
        :param Array operations:  array of operations
    """

    known_chains = known_chains
    default_prefix = "GPH"
    operation_klass = Operation

    def detail(self, *args, **kwargs):
        if "signatures" not in kwargs:  # pragma: no branch
            kwargs["signatures"] = Array([])
        else:  # pragma: no cover
            kwargs["signatures"] = Array(
                [Signature(unhexlify(a)) for a in kwargs["signatures"]]
            )

        ops = kwargs.get("operations", [])
        opklass = self.getOperationKlass()
        if all([not isinstance(a, opklass) for a in ops]):
            kwargs["operations"] = Array([opklass(a) for a in ops])
        else:
            kwargs["operations"] = Array(ops)

        return OrderedDict(
            [
                ("ref_block_num", Uint16(kwargs["ref_block_num"])),
                ("ref_block_prefix", Uint32(kwargs["ref_block_prefix"])),
                ("expiration", PointInTime(kwargs["expiration"])),
                ("operations", kwargs["operations"]),
                ("extensions", Set([])),
                ("signatures", kwargs["signatures"]),
            ]
        )

    def getKnownChains(self):
        return self.known_chains

    def get_default_prefix(self):
        return self.default_prefix

    def getOperationKlass(self):
        return self.operation_klass

    @property
    def id(self):
        """ The transaction id of this transaction
        """
        # Store signatures temporarily since they are not part of
        # transaction id
        sigs = self.data["signatures"]
        self.data.pop("signatures", None)

        # Generage Hash of the seriliazed version
        h = hashlib.sha256(bytes(self)).digest()

        # recover signatures
        self.data["signatures"] = sigs

        # Return properly truncated tx hash
        return hexlify(h[:20]).decode("ascii")

    #     def derSigToHexSig(self, s):
    #         """ Format DER to HEX signature
    #         """
    #         s, junk = ecdsa.der.remove_sequence(unhexlify(s))
    #         if junk:
    #             log.debug('JUNK: %s', hexlify(junk).decode('ascii'))
    #         assert(junk == b'')
    #         x, s = ecdsa.der.remove_integer(s)
    #         y, s = ecdsa.der.remove_integer(s)
    #         return '%064x%064x' % (x, y)

    def getChainParams(self, chain):
        # chain may be an identifier, the chainid, or the prefix
        # ultimately, we need to be able to identify the chain id
        def find_in_known_chains(identifier):
            chains = self.getKnownChains()
            for _id, chain in chains.items():
                if _id == identifier:
                    return chain
                for key, value in chain.items():
                    if value == identifier:
                        return chain

        # Which network are we on:
        my_chain = find_in_known_chains(chain)
        if my_chain:
            chain_params = my_chain
        elif isinstance(chain, dict):
            chain_params = chain
        else:
            raise ValueError("sign() only takes a string or a dict as chain!")
        if "chain_id" not in chain_params:
            raise ValueError("sign() needs a 'chain_id' in chain params!")
        return chain_params

    def deriveDigest(self, chain):
        chain_params = self.getChainParams(chain)
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

    def verify(self, pubkeys=[], chain=None):
        if not chain:
            chain = self.get_default_prefix()

        chain_params = self.getChainParams(chain)
        self.deriveDigest(chain)
        signatures = self.data["signatures"].data
        pubKeysFound = []

        for signature in signatures:
            p = verify_message(self.message, bytes(signature))
            phex = hexlify(p).decode("ascii")
            pubKeysFound.append(phex)

        for pubkey in pubkeys:
            if not isinstance(pubkey, PublicKey):
                raise ValueError("Pubkeys must be array of 'PublicKey'")

            k = pubkey.unCompressed()[2:]
            if k not in pubKeysFound and repr(pubkey) not in pubKeysFound:
                k = PublicKey(PublicKey(k).compressed())
                f = format(k, chain_params["prefix"])
                raise MissingSignatureForKey("Signature for %s missing!" % f)
        return pubKeysFound

    def sign(self, wifkeys, chain=None):
        """ Sign the transaction with the provided private keys.

            :param array wifkeys: Array of wif keys
            :param str chain: identifier for the chain

        """
        if not chain:
            chain = self.get_default_prefix()
        self.deriveDigest(chain)

        # Get Unique private keys
        self.privkeys = []
        for item in wifkeys:
            if item not in self.privkeys:
                self.privkeys.append(item)

        # Sign the message with every private key given!
        sigs = []
        for wif in self.privkeys:
            signature = sign_message(self.message, wif)
            sigs.append(Signature(signature))

        self.data["signatures"] = Array(sigs)
        return self
