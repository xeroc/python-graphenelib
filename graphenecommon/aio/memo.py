# -*- coding: utf-8 -*-
from asyncinit import asyncinit
from ..memo import Memo as SyncMemo


@asyncinit
class Memo(SyncMemo):
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

            from .memo import Memo
            m = await Memo("from-account", "to-account")
            m.blockchain.wallet.unlock("secret")
            enc = (m.encrypt("foobar"))
            print(enc)
            >> {'nonce': '17329630356955254641', 'message': '8563e2bb2976e0217806d642901a2855'}
            print(m.decrypt(enc))
            >> foobar

        To decrypt a memo, simply use

        .. code-block:: python

            from memo import Memo
            m = await Memo()
            m.blockchain.wallet.unlock("secret")
            print(memo.decrypt(op_data["memo"]))

        if ``op_data`` being the payload of a transfer operation.

    """

    async def __init__(self, from_account=None, to_account=None, **kwargs):
        self.define_classes()
        assert self.account_class
        assert self.privatekey_class
        assert self.publickey_class

        if to_account:
            self.to_account = await self.account_class(
                to_account, blockchain_instance=self.blockchain
            )
        if from_account:
            self.from_account = await self.account_class(
                from_account, blockchain_instance=self.blockchain
            )
