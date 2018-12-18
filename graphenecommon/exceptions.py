# -*- coding: utf-8 -*-
class WalletExists(Exception):
    """ A wallet has already been created and requires a password to be
        unlocked by means of :func:`wallet.unlock`.
    """

    pass


class WalletLocked(Exception):
    """ Wallet is locked
    """

    pass


class OfflineHasNoRPCException(Exception):
    """ When in offline mode, we don't have RPC
    """

    pass


class NoWalletException(Exception):
    """ No Wallet could be found, please use :func:`wallet.create` to
        create a new wallet
    """

    pass


class KeyNotFound(Exception):
    """ Key not found
    """

    pass


class KeyAlreadyInStoreException(Exception):
    """ The key is already stored in the store
    """

    pass


class InvalidWifError(Exception):
    """ The provided private Key has an invalid format
    """

    pass


class WorkerDoesNotExistsException(Exception):
    """ Worker does not exist
    """

    pass


class WitnessDoesNotExistsException(Exception):
    """ The witness does not exist
    """

    pass


class VestingBalanceDoesNotExistsException(Exception):
    pass


class InsufficientAuthorityError(Exception):
    pass


class AssetDoesNotExistsException(Exception):
    pass


class AccountDoesNotExistsException(Exception):
    pass


class InvalidAssetException(Exception):
    pass


class BlockDoesNotExistsException(Exception):
    pass


class CommitteeMemberDoesNotExistsException(Exception):
    pass


class MissingKeyError(Exception):
    pass


class InvalidMemoKeyException(Exception):
    pass


class InvalidMessageSignature(Exception):
    pass


class WrongMemoKey(Exception):
    """ The memo provided is not equal the one on the blockchain
    """

    pass


class ProposalDoesNotExistException(Exception):
    pass


class GenesisBalanceDoesNotExistsException(Exception):
    pass
