from .base import (
    InRamConfigurationStore,
    InRamPlainKeyStore,
    InRamEncryptedKeyStore,
    SqliteConfigurationStore,
    SqlitePlainKeyStore,
    SqliteEncryptedKeyStore
)
from .sqlite import SQLiteFile

__all__ = [
    "base",
    "sqlite",
    "ram"
]


def get_default_config_store(*args, **kwargs):
    return SqliteConfigurationStore(*args, **kwargs)
