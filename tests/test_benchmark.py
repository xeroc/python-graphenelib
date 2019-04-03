# -*- coding: utf-8 -*-
import time
from .fixtures import (
    Base58,
    base58decode,
    base58encode,
    ripemd160,
    base58CheckEncode,
    base58CheckDecode,
    gphBase58CheckEncode,
    gphBase58CheckDecode,
)

wif_base58 = "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ"
wif_hex = "800c28fca386c7a227600b2fe50b7cae11ec86d3bf1fbe471be89827e19d72aa1d507a5b8d"
wif_hex_raw = "0c28fca386c7a227600b2fe50b7cae11ec86d3bf1fbe471be89827e19d72aa1d"
wif_gphbase85 = "6Mcb23muAxyXaSMhmB6B1mqkvLdWhtuFZmnZsxDczHRv4mL6Y"


def benchmark_base58():
    return (base58decode(wif_base58), base58encode(wif_hex))


def benchmark_base58check():
    return (base58CheckDecode(wif_base58), base58CheckEncode(0x80, wif_hex_raw))


def benchmark_gphbase58check():
    return (gphBase58CheckDecode(wif_gphbase85), gphBase58CheckEncode(wif_hex_raw))


def test_base58(benchmark):
    a, b = benchmark(benchmark_base58)
    assert a == wif_hex
    assert b == wif_base58


def test_base58check(benchmark):
    a, b = benchmark(benchmark_base58check)
    print(a, b)
    assert a == wif_hex_raw
    assert b == wif_base58


def test_gphbase58check(benchmark):
    a, b = benchmark(benchmark_gphbase58check)
    assert a == wif_hex_raw
    assert b == wif_gphbase85
