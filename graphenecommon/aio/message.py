# -*- coding: utf-8 -*-
import json
import logging
import re
import inspect

from binascii import hexlify, unhexlify
from datetime import datetime
from asyncinit import asyncinit

from graphenebase.ecdsa import sign_message, verify_message

from ..exceptions import (
    AccountDoesNotExistsException,
    InvalidMemoKeyException,
    InvalidMessageSignature,
    WrongMemoKey,
)
from ..message import (
    MessageV1 as SyncMessageV1,
    MessageV2 as SyncMessageV2,
    Message as SyncMessage,
)


log = logging.getLogger(__name__)


@asyncinit
class MessageV1(SyncMessageV1):
    """ Allow to sign and verify Messages that are sigend with a private key
    """

    async def __init__(self, *args, **kwargs):
        # __init__ should be async because AbstractBlockchainInstanceProvider expects async __init__
        super().__init__(*args, **kwargs)

    async def sign(self, account=None, **kwargs):
        """ Sign a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)
            :raises ValueError: If not account for signing is provided

            :returns: the signed message encapsulated in a known format
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        # Data for message
        account = await self.account_class(account, blockchain_instance=self.blockchain)
        info = await self.blockchain.info()
        meta = dict(
            timestamp=info["time"],
            block=info["head_block_number"],
            memokey=account["options"]["memo_key"],
            account=account["name"],
        )

        # wif key
        wif = self.blockchain.wallet.getPrivateKeyForPublicKey(
            account["options"]["memo_key"]
        )

        # We strip the message here so we know for sure there are no trailing
        # whitespaces or returns
        message = self.message.strip()

        enc_message = self.SIGNED_MESSAGE_META.format(**locals())

        # signature
        signature = hexlify(sign_message(enc_message, wif)).decode("ascii")

        self.signed_by_account = account
        self.signed_by_name = account["name"]
        self.meta = meta
        self.plain_message = message

        return self.SIGNED_MESSAGE_ENCAPSULATED.format(
            MESSAGE_SPLIT=self.MESSAGE_SPLIT, **locals()
        )

    async def verify(self, **kwargs):
        """ Verify a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)

            :returns: True if the message is verified successfully
            :raises InvalidMessageSignature if the signature is not ok
        """
        # Split message into its parts
        parts = re.split("|".join(self.MESSAGE_SPLIT), self.message)
        parts = [x for x in parts if x.strip()]

        assert len(parts) > 2, "Incorrect number of message parts"

        # Strip away all whitespaces before and after the message
        message = parts[0].strip()
        signature = parts[2].strip()
        # Parse the meta data
        meta = dict(re.findall(r"(\S+)=(.*)", parts[1]))

        log.info("Message is: {}".format(message))
        log.info("Meta is: {}".format(json.dumps(meta)))
        log.info("Signature is: {}".format(signature))

        # Ensure we have all the data in meta
        assert "account" in meta, "No 'account' could be found in meta data"
        assert "memokey" in meta, "No 'memokey' could be found in meta data"
        assert "block" in meta, "No 'block' could be found in meta data"
        assert "timestamp" in meta, "No 'timestamp' could be found in meta data"

        account_name = meta.get("account").strip()
        memo_key = meta["memokey"].strip()

        try:
            self.publickey_class(memo_key, prefix=self.blockchain.prefix)
        except Exception:
            raise InvalidMemoKeyException("The memo key in the message is invalid")

        # Load account from blockchain
        try:
            account = await self.account_class(
                account_name, blockchain_instance=self.blockchain
            )
        except AccountDoesNotExistsException:
            raise AccountDoesNotExistsException(
                "Could not find account {}. Are you connected to the right chain?".format(
                    account_name
                )
            )

        # Test if memo key is the same as on the blockchain
        if not account["options"]["memo_key"] == memo_key:
            raise WrongMemoKey(
                "Memo Key of account {} on the Blockchain ".format(account["name"])
                + "differs from memo key in the message: {} != {}".format(
                    account["options"]["memo_key"], memo_key
                )
            )

        # Reformat message
        enc_message = self.SIGNED_MESSAGE_META.format(**locals())

        # Verify Signature
        pubkey = verify_message(enc_message, unhexlify(signature))

        # Verify pubky
        pk = self.publickey_class(
            hexlify(pubkey).decode("ascii"), prefix=self.blockchain.prefix
        )
        if format(pk, self.blockchain.prefix) != memo_key:
            raise InvalidMessageSignature("The signature doesn't match the memo key")

        self.signed_by_account = account
        self.signed_by_name = account["name"]
        self.meta = meta
        self.plain_message = message

        return True


@asyncinit
class MessageV2(SyncMessageV2):
    """ Allow to sign and verify Messages that are sigend with a private key
    """

    async def __init__(self, *args, **kwargs):
        # __init__ should be async because AbstractBlockchainInstanceProvider expects async __init__
        super().__init__(*args, **kwargs)

    async def sign(self, account=None, **kwargs):
        """ Sign a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)
            :raises ValueError: If not account for signing is provided

            :returns: the signed message encapsulated in a known format
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        # Data for message
        account = await self.account_class(account, blockchain_instance=self.blockchain)

        # wif key
        wif = self.blockchain.wallet.getPrivateKeyForPublicKey(
            account["options"]["memo_key"]
        )

        payload = [
            "from",
            account["name"],
            "key",
            account["options"]["memo_key"],
            "time",
            str(datetime.utcnow()),
            "text",
            self.message,
        ]
        enc_message = json.dumps(payload, separators=(",", ":"))

        # signature
        signature = hexlify(sign_message(enc_message, wif)).decode("ascii")

        return dict(signed=enc_message, payload=payload, signature=signature)

    async def verify(self, **kwargs):
        """ Verify a message with an account's memo key

            :param str account: (optional) the account that owns the bet
                (defaults to ``default_account``)

            :returns: True if the message is verified successfully
            :raises InvalidMessageSignature if the signature is not ok
        """
        if not isinstance(self.message, dict):
            try:
                self.message = json.loads(self.message)
            except Exception:
                raise ValueError("Message must be valid JSON")

        payload = self.message.get("payload")
        assert payload, "Missing payload"
        payload_dict = {k[0]: k[1] for k in zip(payload[::2], payload[1::2])}
        signature = self.message.get("signature")

        account_name = payload_dict.get("from").strip()
        memo_key = payload_dict.get("key").strip()

        assert account_name, "Missing account name 'from'"
        assert memo_key, "missing 'key'"

        try:
            self.publickey_class(memo_key, prefix=self.blockchain.prefix)
        except Exception:
            raise InvalidMemoKeyException("The memo key in the message is invalid")

        # Load account from blockchain
        try:
            account = await self.account_class(
                account_name, blockchain_instance=self.blockchain
            )
        except AccountDoesNotExistsException:
            raise AccountDoesNotExistsException(
                "Could not find account {}. Are you connected to the right chain?".format(
                    account_name
                )
            )

        # Test if memo key is the same as on the blockchain
        if not account["options"]["memo_key"] == memo_key:
            raise WrongMemoKey(
                "Memo Key of account {} on the Blockchain ".format(account["name"])
                + "differs from memo key in the message: {} != {}".format(
                    account["options"]["memo_key"], memo_key
                )
            )

        # Ensure payload and signed match
        signed_target = json.dumps(self.message.get("payload"), separators=(",", ":"))
        signed_actual = self.message.get("signed")
        assert (
            signed_target == signed_actual
        ), "payload doesn't match signed message: \n{}\n{}".format(
            signed_target, signed_actual
        )

        # Reformat message
        enc_message = self.message.get("signed")

        # Verify Signature
        pubkey = verify_message(enc_message, unhexlify(signature))

        # Verify pubky
        pk = self.publickey_class(
            hexlify(pubkey).decode("ascii"), prefix=self.blockchain.prefix
        )
        if format(pk, self.blockchain.prefix) != memo_key:
            raise InvalidMessageSignature("The signature doesn't match the memo key")

        self.signed_by_account = account
        self.signed_by_name = account["name"]
        self.plain_message = payload_dict.get("text")

        return True


@asyncinit
class Message(SyncMessage, MessageV1, MessageV2):
    supported_formats = (MessageV1, MessageV2)
    valid_exceptions = (
        AccountDoesNotExistsException,
        InvalidMessageSignature,
        WrongMemoKey,
        InvalidMemoKeyException,
    )

    async def __init__(self, *args, **kwargs):
        for _format in self.supported_formats:
            try:
                await _format.__init__(self, *args, **kwargs)
                return
            except self.valid_exceptions as e:
                raise e
            except Exception as e:
                log.warning(
                    "{}: Couldn't init: {}: {}".format(
                        _format.__name__, e.__class__.__name__, str(e)
                    )
                )

    async def verify(self, **kwargs):
        for _format in self.supported_formats:
            try:
                return await _format.verify(self, **kwargs)
            except self.valid_exceptions as e:
                raise e
            except Exception as e:
                log.warning(
                    "{}: Couldn't verify: {}: {}".format(
                        _format.__name__, e.__class__.__name__, str(e)
                    )
                )
        raise ValueError("No Decoder accepted the message")

    async def sign(self, *args, **kwargs):
        for _format in self.supported_formats:
            try:
                return await _format.sign(self, *args, **kwargs)
            except self.valid_exceptions as e:
                raise e
            except Exception as e:
                log.warning(
                    "{}: Couldn't sign: {}: {}".format(
                        _format.__name__, e.__class__.__name__, str(e)
                    )
                )
        raise ValueError("No Decoder accepted the message")
