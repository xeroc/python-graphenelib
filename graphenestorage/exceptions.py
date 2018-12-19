# -*- coding: utf-8 -*-
class WalletLocked(Exception):
    pass


class WrongMasterPasswordException(Exception):
    """ The password provided could not properly unlock the wallet
    """

    pass


class KeyAlreadyInStoreException(Exception):
    """ The key of a key/value pair is already in the store
    """

    pass
