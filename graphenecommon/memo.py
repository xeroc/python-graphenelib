# -*- coding: utf-8 -*-
import random
from graphenebase import memo
from .exceptions import KeyNotFound, MissingKeyError
from .instance import AbstractBlockchainInstanceProvider


class Memo(AbstractBlockchainInstanceProvider):
    """ Deals with Memos that are attached to a transfer

        :param .account.Account from_account: Account that has sent
            the memo
        :param .account.Account to_account: Account that has received
            the memo
        :param instance blockchain_instance: instance to use when accesing a RPC

        A memo is encrypted with a shared secret derived from a private key of
        the sender and a public key of the receiver. Due to the underlying
        mathematics, the same shared secret can be derived by the private key
        of the receiver and the public key of the sender. The encrypted message
        is perturbed by a nonce that is part of the transmitted message.

        .. code-block:: python

            from bitshares.memo import Memo
            m = Memo("bitshareseu", "wallet.xeroc")
            m.blockchain.wallet.unlock("secret")
            enc = (m.encrypt("foobar"))
            print(enc)
            >> {'nonce': '17329630356955254641', 'message': '8563e2bb2976e0217806d642901a2855'}
            print(m.decrypt(enc))
            >> foobar

        To decrypt a memo, simply use

        .. code-block:: python

            from bitshares.memo import Memo
            m = Memo()
            m.blockchain.wallet.unlock("secret")
            print(memo.decrypt(op_data["memo"]))

        if ``op_data`` being the payload of a transfer operation.

    """

    def __init__(self, from_account=None, to_account=None, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.privatekey_class
        assert self.publickey_class

        if to_account:
            self.to_account = self.account_class(
                to_account, blockchain_instance=self.blockchain
            )
        if from_account:
            self.from_account = self.account_class(
                from_account, blockchain_instance=self.blockchain
            )

    def unlock_wallet(self, *args, **kwargs):
        """ Unlock the library internal wallet
        """
        self.blockchain.wallet.unlock(*args, **kwargs)
        return self

    def encrypt(self, message):
        """ Encrypt a memo

            :param str message: clear text memo message
            :returns: encrypted message
            :rtype: str
        """
        if not message:
            return None

        nonce = str(random.getrandbits(64))
        try:
            memo_wif = self.blockchain.wallet.getPrivateKeyForPublicKey(
                self.from_account["options"]["memo_key"]
            )
        except KeyNotFound:
            # if all fails, raise exception
            raise MissingKeyError(
                "Memo private key {} for {} could not be found".format(
                    self.from_account["options"]["memo_key"], self.from_account["name"]
                )
            )
        if not memo_wif:
            raise MissingKeyError(
                "Memo key for %s missing!" % self.from_account["name"]
            )

        if not hasattr(self, "chain_prefix"):
            self.chain_prefix = self.blockchain.prefix

        enc = memo.encode_memo(
            self.privatekey_class(memo_wif),
            self.publickey_class(
                self.to_account["options"]["memo_key"], prefix=self.chain_prefix
            ),
            nonce,
            message,
        )

        return {
            "message": enc,
            "nonce": nonce,
            "from": self.from_account["options"]["memo_key"],
            "to": self.to_account["options"]["memo_key"],
        }

    def decrypt(self, message):
        """ Decrypt a message

            :param str message: encrypted memo message
            :returns: decrypted message
            :rtype: str
        """
        if not message:
            return None

        # We first try to decode assuming we received the memo
        try:
            memo_wif = self.blockchain.wallet.getPrivateKeyForPublicKey(memo["to"])
            pubkey = message["from"]
        except KeyNotFound:
            try:
                # if that failed, we assume that we have sent the memo
                memo_wif = self.blockchain.wallet.getPrivateKeyForPublicKey(
                    message["from"]
                )
                pubkey = message["to"]
            except KeyNotFound:
                # if all fails, raise exception
                raise MissingKeyError(
                    "None of the required memo keys are installed!"
                    "Need any of {}".format([message["to"], message["from"]])
                )

        if not hasattr(self, "chain_prefix"):
            self.chain_prefix = self.blockchain.prefix

        return memo.decode_memo(
            self.privatekey_class(memo_wif),
            self.publickey_class(pubkey, prefix=self.chain_prefix),
            message.get("nonce"),
            message.get("message"),
        )
