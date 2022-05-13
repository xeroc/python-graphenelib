# -*- coding: utf-8 -*-
import ecdsa
import sys
import unittest
import hashlib
from .fixtures import (
    Base58,
    BrainKey,
    Address,
    PublicKey,
    PrivateKey,
    PasswordKey,
    GrapheneAddress,
    BitcoinAddress,
)


class Testcases(unittest.TestCase):
    def test_B85hexgetb58_btc(self):
        self.assertEqual(
            [
                "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",
                "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S",
                "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49",
                "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131",
                "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e",
                "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e",
            ],
            [
                format(
                    Base58(
                        "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"
                    ),
                    "WIF",
                ),
                format(
                    Base58(
                        "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"
                    ),
                    "WIF",
                ),
                format(
                    Base58(
                        "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"
                    ),
                    "WIF",
                ),
                format(
                    Base58(
                        "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"
                    ),
                    "WIF",
                ),
                format(
                    Base58(
                        "b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"
                    ),
                    "WIF",
                ),
                repr(Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")),
                repr(Base58("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")),
                repr(Base58("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                repr(Base58("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
            ],
        )

    def test_B85hexgetb58(self):
        self.assertEqual(
            [
                "BTS2CAbTi1ZcgMJ5otBFZSGZJKJenwGa9NvkLxsrS49Kr8JsiSGc",
                "BTShL45FEyUVSVV1LXABQnh4joS9FsUaffRtsdarB5uZjPsrwMZF",
                "BTS7DQR5GsfVaw4wJXzA3TogDhuQ8tUR2Ggj8pwyNCJXheHehL4Q",
                "BTSqc4QMAJHAkna65i8U4b7nkbWk4VYSWpZebW7JBbD7MN8FB5sc",
                "BTS2QAVTJnJQvLUY4RDrtxzX9jS39gEq8gbqYMWjgMxvsvZTJxDSu",
            ],
            [
                format(
                    Base58(
                        "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"
                    ),
                    "BTS",
                ),
                format(
                    Base58(
                        "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"
                    ),
                    "BTS",
                ),
                format(
                    Base58(
                        "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"
                    ),
                    "BTS",
                ),
                format(
                    Base58(
                        "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"
                    ),
                    "BTS",
                ),
                format(
                    Base58(
                        "b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"
                    ),
                    "BTS",
                ),
            ],
        )

    def test_Address(self):
        self.assertEqual(
            [
                format(
                    Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi", prefix="BTS"), "BTS"
                ),
                format(
                    Address("BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112", prefix="BTS"), "BTS"
                ),
                format(
                    Address("BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk", prefix="BTS"), "BTS"
                ),
                format(
                    Address("BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL", prefix="BTS"), "BTS"
                ),
                format(
                    Address("BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr", prefix="BTS"), "BTS"
                ),
            ],
            [
                "BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi",
                "BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112",
                "BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk",
                "BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL",
                "BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr",
            ],
        )

        self.assertEqual(
            [
                bytes(Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi", prefix="BTS")),
                bytes(Address("BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112", prefix="BTS")),
                bytes(Address("BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk", prefix="BTS")),
                bytes(Address("BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL", prefix="BTS")),
                bytes(Address("BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr", prefix="BTS")),
            ],
            [
                b"\x9d\x91\xe1}\xa7\x8ff\xd9\xfb\x1b\xd6P\x9c\x97\xc5\x96\xee\x95\x81]",
                b"\x06\xe8\xbc\x1f\xf1P\xad\x9f-4^v5\xc1^\xc9\xac\xf0\xa4\xac",
                b"\xbe\xeab\xd8K\x94t\xfe^#M\x89\x84\xbcO\xc4x\x1d\x8aU",
                b"\x9d\xd4d\x07\xc1\xc6qa7\x1e\xf0\x9b\xef\xbb\x05E\x14,\x98\xa2",
                b"\x1f\x1e\x13\x17\xcay\x82\xe9\xb3pe a\x15(\xea7\x98\x1a\xe1",
            ],
        )

        self.assertEqual(
            [
                bytes(
                    GrapheneAddress.from_pubkey(
                        PublicKey(
                            "BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                            prefix="BTS",
                        ),
                        prefix="BTS",
                    )
                ),
                bytes(
                    GrapheneAddress.from_pubkey(
                        PublicKey(
                            "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                            prefix="BTS",
                        ),
                        prefix="BTS",
                    )
                ),
                bytes(
                    GrapheneAddress.from_pubkey(
                        PublicKey(
                            "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                            prefix="BTS",
                        ),
                        prefix="BTS",
                    )
                ),
                bytes(
                    GrapheneAddress.from_pubkey(
                        PublicKey(
                            "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                            prefix="BTS",
                        ),
                        prefix="BTS",
                        compressed=True,
                    )
                ),
                bytes(
                    GrapheneAddress.from_pubkey(
                        PublicKey(
                            "GPH7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra"
                        ),
                        compressed=False,
                    )
                ),
            ],
            [
                b"7\xd6\x90p+B\xe9r\xf4\xd1-[\xea\x1f<\xbe#m\xbdu",
                b"\xc9\x92\x97b\x7f\xc0u9\xd2\x9a\xe4E=\x81\xeb\x96l\xcf(3",
                b"M/\xbf\x83\xac\x9f\xff\xf6\xcf=\x9e@\xd45U\x91\xfe\xda\xf26",
                b"\xef\xf8\x9e\xa7\x8ei:\x83L\xc57\xaa*4\xdb\x9ff\xbcs\xf6",
                b"\x0f\xec\xc4I\x8a\xfbUAg\xa5\xe9\xb5\xac\xea\x1dJ\x14\x87\x11\xf7",
            ],
        )

    def test_PubKey(self):
        self.assertEqual(
            [
                format(
                    PublicKey(
                        "BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                        prefix="BTS",
                    ).address,
                    "BTS",
                ),
                format(
                    PublicKey(
                        "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                        prefix="BTS",
                    ).address,
                    "BTS",
                ),
                format(
                    PublicKey(
                        "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                        prefix="BTS",
                    ).address,
                    "BTS",
                ),
                format(
                    PublicKey(
                        "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                        prefix="BTS",
                    ).address,
                    "BTS",
                ),
                format(
                    PublicKey(
                        "BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",
                        prefix="BTS",
                    ).address,
                    "BTS",
                ),
            ],
            [
                "BTS66FCjYKzMwLbE3a59YpmFqA9bwporT4L3",
                "BTSKNpRuPX8KhTBsJoFp1JXd7eQEsnCpRw3k",
                "BTS838ENJargbUrxXWuE2xD9HKjQaS17GdCd",
                "BTSNsrLFWTziSZASnNJjWafFtGBfSu8VG8KU",
                "BTSDjAGuXzk3WXabBEgKKc8NsuQM412boBdR",
            ],
        )

    def test_btsprivkey(self):
        self.assertEqual(
            [
                format(
                    PrivateKey(
                        Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")
                    ).address,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S"
                    ).address,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                    ).address,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                    ).address,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                    ).address,
                    "BTS",
                ),
            ],
            [
                "BTSGu2U7Q3rmkCUCkQH2SToLMjEVUr86GrpA",
                "BTS9YgTfC8EfkgDG7DoRXJpMVKRougo64Lop",
                "BTSBXqRucGm7nRkk6jm7BNspTJTWRtNcx7k5",
                "BTS5tTDDR6M3mkcyVv16edsw8dGUyNQZrvKU",
                "BTS8G9ATJbJewVjTgTGmLGLNe1uP5XDWzaKX",
            ],
        )

    def test_btsprivkey_change_prefix(self):
        class P(PrivateKey):
            prefix = "GGG"

        self.assertEqual(
            [
                str(
                    P(
                        Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")
                    ).address
                ),
                str(P("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S").address),
                str(P("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq").address),
                str(P("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R").address),
                str(P("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7").address),
            ],
            [
                "GGGGu2U7Q3rmkCUCkQH2SToLMjEVUr86GrpA",
                "GGG9YgTfC8EfkgDG7DoRXJpMVKRougo64Lop",
                "GGGBXqRucGm7nRkk6jm7BNspTJTWRtNcx7k5",
                "GGG5tTDDR6M3mkcyVv16edsw8dGUyNQZrvKU",
                "GGG8G9ATJbJewVjTgTGmLGLNe1uP5XDWzaKX",
            ],
        )

    def test_uncompressed_privatekey(self):
        self.assertEqual(
            [
                format(
                    PrivateKey(
                        Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")
                    ).uncompressed,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S"
                    ).uncompressed,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                    ).uncompressed,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                    ).uncompressed,
                    "BTS",
                ),
                format(
                    PrivateKey(
                        "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                    ).uncompressed,
                    "BTS",
                ),
            ],
            [
                "BTS677ZZd62Ca7SoUJoT1CytBhj4aJewzzi8tQZxYNqpSSK69FTuF",
                "BTS5z5e3BawwMY6UmcBQxYpkKZ8QQm4wdtS4KMZiWAcWBUC3RJuLT",
                "BTS7W5qsanXHgRAZPijbrLMDwX6VmHqUdL2s8PZiYKD5h1R7JaqRJ",
                "BTS86qPFWptPfUNKVi6hemeEWshoLerN6JvzCvFjqnRSEJg7nackU",
                "BTS57qhJwt9hZtBsGgV7J5ZPHFi5r5MEeommYnFpDb6grK3qev2qX",
            ],
        )

    def test_get_secret(self):
        self.maxDiff = None
        self.assertEqual(
            [
                PrivateKey(
                    "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S"
                ).get_secret(),
                PrivateKey(
                    "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                ).get_secret(),
                PrivateKey(
                    "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                ).get_secret(),
                PrivateKey(
                    "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                ).get_secret(),
            ],
            [
                b'\xf4\x8d\xeb\xee\x1b\x00\xab\xc0\x07xIu\xcf\xd3:X\x88b\x86\xc8\xeeD\x1c~a\xf0j"\xbb\xb1t.',
                b"\xdc\x86\xb1&\x82\xfdF\x8a\xd3*\x85\xfa\x05\x1d\xd6_\x00\xdc\x88\x93\x1e\xcb\x11\x82\xc35\x01\xf4\xce\xdc\xc3\x94",
                b'g\x13\x80\x85*\x17d7C\xa3X\xbc\x18G\xd3\x08\xee\x02<("(\x9a\xc2WB]\x89\x13\xd9Z\x97',
                b"Q?\xa0\x9e\xc7\xae\xcb\x1a\x1c,\xa5'\x8b\x0e;\x84I\xc2\x9a\xb0\x8ay\x9d@\xfa\xd7\xe4\x9d\xfbj\x1eD",
            ],
        )

    def test_PublicKey(self):
        self.assertEqual(
            [
                str(
                    PublicKey(
                        "BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                        prefix="BTS",
                    )
                ),
                str(
                    PublicKey(
                        "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                        prefix="BTS",
                    )
                ),
                str(
                    PublicKey(
                        "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                        prefix="BTS",
                    )
                ),
                str(
                    PublicKey(
                        "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                        prefix="BTS",
                    )
                ),
                str(
                    PublicKey(
                        "BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",
                        prefix="BTS",
                    ).pubkey
                ),
                str(
                    PublicKey(
                        "BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",
                        prefix="BTS",
                    ).compressed_key
                ),
            ],
            [
                "BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                "7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",
                "GPH7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra",
            ],
        )

    def test_Privatekey(self):
        self.assertEqual(
            [
                format(
                    PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"),
                    "wif",
                ),
                str(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                str(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
                repr(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                repr(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                repr(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
            ],
            [
                "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e",
                "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e",
                "b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8",
            ],
        )

    def test_BrainKey(self):
        self.assertEqual(
            [
                str(
                    BrainKey(
                        "COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "NAK TILTING MOOTING TAVERT SCREENY MAGIC BARDIE UPBORNE CONOID MAUVE CARBON NOTAEUM BITUMEN HOOEY KURUMA COWFISH"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "CORKITE CORDAGE FONDISH UNDER FORGET BEFLEA OUTBUD ZOOGAMY BERLINE ACANTHA STYLO YINCE TROPISM TUNKET FALCULA TOMENT"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "MURZA PREDRAW FIT LARIGOT CRYOGEN SEVENTH LISP UNTAWED AMBER CRETIN KOVIL TEATED OUTGRIN POTTAGY KLAFTER DABB"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "VERDICT REPOUR SUNRAY WAMBLY UNFILM UNCOUS COWMAN REBUOY MIURUS KEACORN BENZOLE BEMAUL SAXTIE DOLENT CHABUK BOUGHED"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "HOUGH TRUMPH SUCKEN EXODY MAMMATE PIGGIN CRIME TEPEE URETHAN TOLUATE BLINDLY CACOEPY SPINOSE COMMIE GRIECE FUNDAL"
                    ).get_private()
                ),
                str(
                    BrainKey(
                        "OERSTED ETHERIN TESTIS PEGGLE ONCOST POMME SUBAH FLOODER OLIGIST ACCUSE UNPLAT OATLIKE DEWTRY CYCLIZE PIMLICO CHICOT"
                    ).get_private()
                ),
            ],
            [
                "5JfwDztjHYDDdKnCpjY6cwUQfM4hbtYmSJLjGd9KTpk9J4H2jDZ",
                "5JcdQEQjBS92rKqwzQnpBndqieKAMQSiXLhU7SFZoCja5c1JyKM",
                "5JsmdqfNXegnM1eA8HyL6uimHp6pS9ba4kwoiWjjvqFC1fY5AeV",
                "5J2KeFptc73WTZPoT1Sd59prFep6SobGobCYm7T5ZnBKtuW9RL9",
                "5HryThsy6ySbkaiGK12r8kQ21vNdH81T5iifFEZNTe59wfPFvU9",
                "5Ji4N7LSSv3MAVkM3Gw2kq8GT5uxZYNaZ3d3y2C4Ex1m7vshjBN",
                "5HqSHfckRKmZLqqWW7p2iU18BYvyjxQs2sksRWhXMWXsNEtxPZU",
            ],
        )

    def test_BrainKey_normalize(self):
        b = "COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO"
        self.assertEqual(
            [
                BrainKey(b + "").get_brainkey(),
                BrainKey(b + " ").get_brainkey(),
                BrainKey(b + "  ").get_brainkey(),
                BrainKey(b + "\t").get_brainkey(),
                BrainKey(b + "\t\t").get_brainkey(),
                BrainKey(b.replace(" ", "\t")).get_brainkey(),
                BrainKey(b.replace(" ", "  ")).get_brainkey(),
            ],
            [b, b, b, b, b, b, b],
        )

    def test_BrainKey_sequences(self):
        b = BrainKey(
            "COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO"
        )
        keys = [
            "5Hsbn6kXio4bb7eW5bX7kTp2sdkmbzP8kGWoau46Cf7en7T1RRE",
            "5K9MHEyiSye5iFL2srZu3ZVjzAZjcQxUgUvuttcVrymovFbU4cc",
            "5JBXhzDWQdYPAzRxxuGtzqM7ULLKPK7GZmktHTyF9foGGfbtDLT",
            "5Kbbfbs6DmJFNddWiP1XZfDKwhm5dkn9KX5AENQfQke2RYBBDcz",
            "5JUqLwgxn8f7myNz4gDwo5e77HZgopHMDHv4icNVww9Rxu1GDG5",
            "5JNBVj5QVh86N8MUUwY3EVUmsZwChZftxnuJx22DzEtHWC4rmvK",
            "5JdvczYtxPPjQdXMki1tpNvuSbvPMxJG5y4ndEAuQsC5RYMQXuC",
            "5HsUSesU2YB4EA3dmpGtHh8aPAwEdkdhidG8hcU2Nd2tETKk85t",
            "5JpveiQd1mt91APyQwvsCdAXWJ7uag3JmhtSxpGienic8vv1k2W",
            "5KDGhQUqQmwcGQ9tegimSyyT4vmH8h2fMzoNe1MT9bEGvRvR6kD",
        ]
        for i in keys:
            p = b.next_sequence().get_private()
            self.assertEqual(str(p), i)

    def test_BrainKey_blind(self):
        b = BrainKey(
            "MATZO COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN"
        )
        key = "5JmdAQbRpV94LDVb2igq6YR5MVj1NVaJxBWpHP9Y6LspmMobbv5"
        p = b.get_blind_private()
        self.assertEqual(str(p), key)

    def test_PasswordKey(self):
        a = [
            "Aang7foN3oz1Ungai2qua5toh3map8ladei1eem2ohsh2shuo8aeji9Thoseo7ah",
            "iep1Mees9eghiifahwei5iidi0Sazae9aigaeT7itho3quoo2dah5zuvobaelau5",
            "ohBeuyoothae5aer9odaegh5Eeloh1fi7obei9ahSh0haeYuas1sheehaiv5LaiX",
            "geiQuoo9NeeLoaZee0ain3Ku1biedohsesien4uHo1eib1ahzaesh5shae3iena7",
            "jahzeice6Ix8ohBo3eik9pohjahgeegoh9sahthai1aeMahs8ki7Iub1oojeeSuo",
            "eiVahHoh2hi4fazah9Tha8loxeeNgequaquuYee6Shoopo3EiWoosheeX6yohg2o",
            "PheeCh3ar8xoofoiphoo4aisahjiiPah4vah0eeceiJ2iyeem9wahyupeithah9T",
            "IuyiibahNgieshei2eeFu8aic1IeMae9ooXi9jaiwaht4Wiengieghahnguang0U",
            "Ipee1quee7sheughemae4eir8pheix3quac3ei0Aquo9ohieLaeseeh8AhGeM2ew",
            "Tech5iir0aP6waiMeiHoph3iwoch4iijoogh0zoh9aSh6Ueb2Dee5dang1aa8IiP",
        ]
        b = [
            "STM5NyCrrXHmdikC6QPRAPoDjSHVQJe3WC5bMZuF6YhqhSsfYfjhN",
            "STM8gyvJtYyv5ZbT2ZxbAtgufQ5ovV2bq6EQp4YDTzQuSwyg7Ckry",
            "STM7yE71iVPSpaq8Ae2AmsKfyFxA8pwYv5zgQtCnX7xMwRUQMVoGf",
            "STM5jRgWA2kswPaXsQNtD2MMjs92XfJ1TYob6tjHtsECg2AusF5Wo",
            "STM6XHwVxcP6zP5NV1jUbG6Kso9m8ZG9g2CjDiPcZpAxHngx6ATPB",
            "STM59X1S4ofTAeHd1iNHDGxim5GkLo2AdcznksUsSYGU687ywB5WV",
            "STM6BPPL4iSRbFVVN8v3BEEEyDsC1STRK7Ba9ewQ4Lqvszn5J8VAe",
            "STM7cdK927wj95ptUrCk6HKWVeF74LG5cTjDTV22Z3yJ4Xw8xc9qp",
            "STM7VNFRjrE1hs1CKpEAP9NAabdFpwvzYXRKvkrVBBv2kTQCbNHz7",
            "STM7ZZFhEBjujcKjkmY31i1spPMx6xDSRhkursZLigi2HKLuALe5t",
        ]
        c = [
            "5Jaa3d8fC4FpiYFGNapPCQZ1id5p9WsMsTEU3N8AjfuH7Wga5nW",
            "5J7xXhZktey6VEcETjc7VkbbeNqDPPhB5iKsZfqfZ4kYDx6qUtZ",
            "5KPiL353VqrCvRTjCBo4A16c1caai9MEZWPoLddoqDozF8Zp1U7",
            "5KE7YercwKDzQtRipD7cTJaXP1d7BGtmdgvHbHgTqCXMC7tWym1",
            "5KfzkwQ2JNTXhxkernFyv5epfCHkPh64W9XG24HQBYMEdnF9wFG",
            "5K554APUTdVL5NbvgSrJz2mwPWqsWU98B71V9oXCkviDGpssMNG",
            "5KAqbJufq9B5GREfKUADU9QiVR7BryatEFSUCP2dBkeE1txwPdy",
            "5JthkzjpiYzCV7o8ArB9i9JtLSfSjU11W1y177d6pt4Vd1eyL2d",
            "5K4uhyNjYYxUG4i5Wx3umUQSsHn2StH86APNLa2tuE9yHqZVHZD",
            "5HwK7gZTrk69vEtnU1hrTsbmVuEAQMehBxtZogojMSoj7jikXhx",
        ]
        for i, pwd in enumerate(a):
            password = PasswordKey("xeroc", pwd, "posting")
            self.assertEqual(format(password.get_public(), "STM"), b[i])
            self.assertEqual(format(password.get_public_key(), "STM"), b[i])
            self.assertEqual(str(password.get_private_key()), c[i])
            self.assertEqual(str(password.get_private()), c[i])

    def test_btcprivkey(self):
        self.assertEqual(
            [
                format(
                    PrivateKey(
                        "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                    ).bitcoin.address,
                    "BTC",
                ),
                format(
                    PrivateKey(
                        "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                    ).bitcoin.address,
                    "BTC",
                ),
                format(
                    PrivateKey(
                        "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                    ).bitcoin.address,
                    "BTC",
                ),
            ],
            [
                "1G7qw8FiVfHEFrSt3tDi6YgfAdrDrEM44Z",
                "12c7KAAZfpREaQZuvjC5EhpoN6si9vekqK",
                "1Gu5191CVHmaoU3Zz3prept87jjnpFDrXL",
            ],
        )

    def test_btcprivkeystr(self):
        self.assertEqual(
            [
                str(
                    BitcoinAddress.from_pubkey(
                        PrivateKey(
                            "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                        ).pubkey
                    )
                ),
                str(
                    BitcoinAddress.from_pubkey(
                        PrivateKey(
                            "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                        ).pubkey,
                        compressed=True,
                    )
                ),
                str(
                    BitcoinAddress.from_pubkey(
                        PrivateKey(
                            "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                        ).pubkey,
                        compressed=False,
                    )
                ),
            ],
            [
                "1G7qw8FiVfHEFrSt3tDi6YgfAdrDrEM44Z",
                "1E2jXCkSmLxirL31gHwi1UWTjUBxCgS7pq",
                "1Gu5191CVHmaoU3Zz3prept87jjnpFDrXL",
            ],
        )

    def test_gphprivkeystr(self):
        self.assertEqual(
            [
                str(
                    Address.from_pubkey(
                        PrivateKey(
                            "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq"
                        ).pubkey
                    )
                ),
                str(
                    Address.from_pubkey(
                        PrivateKey(
                            "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R"
                        ).pubkey
                    )
                ),
                str(
                    Address.from_pubkey(
                        PrivateKey(
                            "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7"
                        ).pubkey,
                        compressed=False,
                        prefix="BTS",
                    )
                ),
            ],
            [
                "GPHBXqRucGm7nRkk6jm7BNspTJTWRtNcx7k5",
                "GPH5tTDDR6M3mkcyVv16edsw8dGUyNQZrvKU",
                "BTS4XPkBqYw882fH5aR5S8mMKXCaZ1yVA76f",
            ],
        )

    def test_password_suggest(self):
        self.assertEqual(len(BrainKey.suggest().split(" ")), 16)

    def test_child(self):
        p = PrivateKey("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")
        p2 = p.child(b"Foobar")
        self.assertIsInstance(p2, PrivateKey)
        self.assertEqual(str(p2), "5JQ6AQmjpbEZjJBLnoa3BaWa9y3LDTUBeSDwEGQD2UjYkb1gY2x")

    """
    @unittest.skipIf(sys.platform.startswith("win"), "skipped due to secp256k1")
    def test_child_pub(self):
        p = PrivateKey("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")
        pub = p.pubkey
        point = pub.point()
        self.assertEqual(
            [
                ecdsa.util.number_to_string(point.x(), ecdsa.SECP256k1.order),
                ecdsa.util.number_to_string(point.y(), ecdsa.SECP256k1.order),
            ],
            [
                b"\x90d5\xf6\xf9\xceo=NL\xf8\xd3\xd0\xdd\xce \x9a\x83'w8\xff\xdc~\xaec\x08\xf4\xed)c\xdf",
                b"\r\xa8tl\xf1:a\x89\xa2\x81\x96\\X\x0fBA]\x86\xe9l#*\x89%\xea\x152T\xbb\x87\x9f`",
            ],
        )
        self.assertEqual(
            repr(pub.child(b"foobar")),
            "022a42ae1e9af8f84544c9a1970308c31f864dfb4f5998c45ef76e11d307cc77d5",
        )
        self.assertEqual(
            repr(pub.add(hashlib.sha256(b"Foobar").digest())),
            "0354a2c06c398990c52933df0c93b9904a4b23b0e2d524a3b0075c72adaa4e459e",
        )
    """

    def test_BrainKey_sequence(self):
        b = BrainKey(
            "COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO"
        )
        b = next(b)
        self.assertEqual(
            str(b.get_private_key()),
            "5Hsbn6kXio4bb7eW5bX7kTp2sdkmbzP8kGWoau46Cf7en7T1RRE",
        )
        self.assertEqual(
            str(b.get_private()), "5Hsbn6kXio4bb7eW5bX7kTp2sdkmbzP8kGWoau46Cf7en7T1RRE"
        )
        self.assertEqual(
            str(b.get_public_key()),
            "GPH6Lduu3V4hoDBeasWrdG45tAGeKG4b7XZFqF4GiryqTNZmWDdW7",
        )
        self.assertEqual(
            str(b.get_public()), "GPH6Lduu3V4hoDBeasWrdG45tAGeKG4b7XZFqF4GiryqTNZmWDdW7"
        )

    def test_new_privatekey(self):
        w = PrivateKey()
        self.assertIsInstance(w, PrivateKey)
        self.assertEqual(str(w)[0], "5")  # is a wif key that starts with 5

    def test_new_BrainKey(self):
        w = BrainKey().get_private_key()
        self.assertIsInstance(w, PrivateKey)
        self.assertEqual(str(w)[0], "5")  # is a wif key that starts with 5

    def test_derive_private_key(self):
        p = PrivateKey("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")
        p2 = p.derive_private_key(10)
        self.assertEqual(
            repr(p2), "2dc7cb99933132e25b37710f9ea806228b04a583da11a137ef97fd42c0007390"
        )

    def test_derive_child(self):
        # NOTE: this key + offset pair is particularly nasty, as
        # the resulting derived value is less then 64 bytes long.
        # Thus, this test also tests for proper padding.
        p = PrivateKey("5K6hMUtQB2xwjuz3SRR6uM5HNERWgBqcK7gPPZ31XtAyBNoATZd")
        p2 = p.child(
            b"\xaf\x8f: \xf6T?V\x0bM\xd8\x16 \xfd\xde\xe9\xb9\xac\x03\r\xba\xb2\x8d\x868-\xc2\x90\x80\xe8\x1b\xce"
        )
        self.assertEqual(
            repr(p2), "0c5fae344a513a4cfab312b24c08df2b2d6afa25c0ead0d3d1d0d3e76794109b"
        )

    def test_init_wrong_format(self):
        with self.assertRaises(NotImplementedError):
            PrivateKey("KJWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")
        with self.assertRaises(NotImplementedError):
            PrivateKey("LJWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")
