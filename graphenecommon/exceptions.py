__all__ = [
    "InvalidWifError",
    "KeyAlreadyInStoreException",
    "KeyNotFound",
    "NoWalletException",
    "OfflineHasNoRPCException",
    "WalletExists",
    "WalletLocked",
]


class WalletExists(Exception):
    """ A wallet has already been created and requires a password to be
        unlocked by means of :func:`bitshares.wallet.unlock`.
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
    """ No Wallet could be found, please use :func:`bitshares.wallet.create` to
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
