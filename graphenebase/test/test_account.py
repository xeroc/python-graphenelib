import unittest
from graphenebase.base58 import Base58
from graphenebase.account import BrainKey, Address, PublicKey, PrivateKey


class Testcases(unittest.TestCase) :
    def test_B85hexgetb58_btc(self):
        self.assertEqual(["5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",
                          "5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S",
                          "5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                          "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                          "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                          "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49",
                          "5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131",
                          "0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e",
                          "6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e",
                          ],
                         [format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"), "WIF"),
                          format(Base58("5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"), "WIF"),
                          format(Base58("0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"), "WIF"),
                          format(Base58("6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"), "WIF"),
                          format(Base58("b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"), "WIF"),
                          repr(Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")),
                          repr(Base58("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S")),
                          repr(Base58("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                          repr(Base58("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                          ])

    def test_B85hexgetb58(self):
        self.assertEqual(['BTS2CAbTi1ZcgMJ5otBFZSGZJKJenwGa9NvkLxsrS49Kr8JsiSGc',
                          'BTShL45FEyUVSVV1LXABQnh4joS9FsUaffRtsdarB5uZjPsrwMZF',
                          'BTS7DQR5GsfVaw4wJXzA3TogDhuQ8tUR2Ggj8pwyNCJXheHehL4Q',
                          'BTSqc4QMAJHAkna65i8U4b7nkbWk4VYSWpZebW7JBbD7MN8FB5sc',
                          'BTS2QAVTJnJQvLUY4RDrtxzX9jS39gEq8gbqYMWjgMxvsvZTJxDSu'
                          ],
                         [format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"), "BTS"),
                          format(Base58("5b921f7051be5e13e177a0253229903c40493df410ae04f4a450c85568f19131"), "BTS"),
                          format(Base58("0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e"), "BTS"),
                          format(Base58("6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e"), "BTS"),
                          format(Base58("b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8"), "BTS")])

    def test_Adress(self):
        self.assertEqual([format(Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi"), "BTS"),
                          format(Address("BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112"), "BTS"),
                          format(Address("BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk"), "BTS"),
                          format(Address("BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL"), "BTS"),
                          format(Address("BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr"), "BTS"),
                          ],
                         ["BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi",
                          "BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112",
                          "BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk",
                          "BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL",
                          "BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr",
                          ])

    def test_PubKey(self):
        self.assertEqual([format(PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL", prefix="BTS").address, "BTS"),
                          format(PublicKey("BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT", prefix="BTS").address, "BTS"),
                          format(PublicKey("BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw", prefix="BTS").address, "BTS"),
                          format(PublicKey("BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V", prefix="BTS").address, "BTS"),
                          format(PublicKey("BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra", prefix="BTS").address, "BTS")
                          ],
                         ["BTS66FCjYKzMwLbE3a59YpmFqA9bwporT4L3",
                          "BTSKNpRuPX8KhTBsJoFp1JXd7eQEsnCpRw3k",
                          "BTS838ENJargbUrxXWuE2xD9HKjQaS17GdCd",
                          "BTSNsrLFWTziSZASnNJjWafFtGBfSu8VG8KU",
                          "BTSDjAGuXzk3WXabBEgKKc8NsuQM412boBdR"
                          ])

    def test_btsprivkey(self):
        self.assertEqual([format(PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd").address, "BTS"),
                          format(PrivateKey("5JWcdkhL3w4RkVPcZMdJsjos22yB5cSkPExerktvKnRNZR5gx1S").address, "BTS"),
                          format(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq").address, "BTS"),
                          format(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R").address, "BTS"),
                          format(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7").address, "BTS")
                          ],
                         ["BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi",
                          "BTSdXrrTXimLb6TEt3nHnePwFmBT6Cck112",
                          "BTSJQUAt4gz4civ8gSs5srTK4r82F7HvpChk",
                          "BTSFPXXHXXGbyTBwdKoJaAPXRnhFNtTRS4EL",
                          "BTS3qXyZnjJneeAddgNDYNYXbF7ARZrRv5dr",
                          ])

    def test_btcprivkey(self):
        self.assertEqual([format(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq").uncompressed.address, "BTC"),
                          format(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R").uncompressed.address, "BTC"),
                          format(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7").uncompressed.address, "BTC"),
                          ],
                         ["1G7qw8FiVfHEFrSt3tDi6YgfAdrDrEM44Z",
                          "12c7KAAZfpREaQZuvjC5EhpoN6si9vekqK",
                          "1Gu5191CVHmaoU3Zz3prept87jjnpFDrXL",
                          ])

    def test_PublicKey(self):
        self.assertEqual([str(PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL", prefix="BTS")),
                          str(PublicKey("BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT", prefix="BTS")),
                          str(PublicKey("BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw", prefix="BTS")),
                          str(PublicKey("BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V", prefix="BTS")),
                          str(PublicKey("BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra", prefix="BTS"))
                          ],
                         ["BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL",
                          "BTS8YAMLtNcnqGNd3fx28NP3WoyuqNtzxXpwXTkZjbfe9scBmSyGT",
                          "BTS7HUo6bm7Gfoi3RqAtzwZ83BFCwiCZ4tp37oZjtWxGEBJVzVVGw",
                          "BTS6676cZ9qmqPnWMrm4McjCuHcnt6QW5d8oRJ4t8EDH8DdCjvh4V",
                          "BTS7u8m6zUNuzPNK1tPPLtnipxgqV9mVmTzrFNJ9GvovvSTCkVUra"
                          ])

    def test_Privatekey(self):
        self.assertEqual([str(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                          str(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                          str(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
                          repr(PrivateKey("5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq")),
                          repr(PrivateKey("5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R")),
                          repr(PrivateKey("5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7")),
                          ],
                         ["5HvVz6XMx84aC5KaaBbwYrRLvWE46cH6zVnv4827SBPLorg76oq",
                          "5Jete5oFNjjk3aUMkKuxgAXsp7ZyhgJbYNiNjHLvq5xzXkiqw7R",
                          "5KDT58ksNsVKjYShG4Ls5ZtredybSxzmKec8juj7CojZj6LPRF7",
                          '0e1bfc9024d1f55a7855dc690e45b2e089d2d825a4671a3c3c7e4ea4e74ec00e',
                          '6e5cc4653d46e690c709ed9e0570a2c75a286ad7c1bc69a648aae6855d919d3e',
                          'b84abd64d66ee1dd614230ebbe9d9c6d66d78d93927c395196666762e9ad69d8'
                          ])

    def test_BrainKey(self):
        self.assertEqual([str(BrainKey("COLORER BICORN KASBEKE FAERIE LOCHIA GOMUTI SOVKHOZ Y GERMAL AUNTIE PERFUMY TIME FEATURE GANGAN CELEMIN MATZO").get_private()),
                          str(BrainKey("NAK TILTING MOOTING TAVERT SCREENY MAGIC BARDIE UPBORNE CONOID MAUVE CARBON NOTAEUM BITUMEN HOOEY KURUMA COWFISH").get_private()),
                          str(BrainKey("CORKITE CORDAGE FONDISH UNDER FORGET BEFLEA OUTBUD ZOOGAMY BERLINE ACANTHA STYLO YINCE TROPISM TUNKET FALCULA TOMENT").get_private()),
                          str(BrainKey("MURZA PREDRAW FIT LARIGOT CRYOGEN SEVENTH LISP UNTAWED AMBER CRETIN KOVIL TEATED OUTGRIN POTTAGY KLAFTER DABB").get_private()),
                          str(BrainKey("VERDICT REPOUR SUNRAY WAMBLY UNFILM UNCOUS COWMAN REBUOY MIURUS KEACORN BENZOLE BEMAUL SAXTIE DOLENT CHABUK BOUGHED").get_private()),
                          str(BrainKey("HOUGH TRUMPH SUCKEN EXODY MAMMATE PIGGIN CRIME TEPEE URETHAN TOLUATE BLINDLY CACOEPY SPINOSE COMMIE GRIECE FUNDAL").get_private()),
                          str(BrainKey("OERSTED ETHERIN TESTIS PEGGLE ONCOST POMME SUBAH FLOODER OLIGIST ACCUSE UNPLAT OATLIKE DEWTRY CYCLIZE PIMLICO CHICOT").get_private()),
                          ],
                         ["5JfwDztjHYDDdKnCpjY6cwUQfM4hbtYmSJLjGd9KTpk9J4H2jDZ",
                          "5JcdQEQjBS92rKqwzQnpBndqieKAMQSiXLhU7SFZoCja5c1JyKM",
                          "5JsmdqfNXegnM1eA8HyL6uimHp6pS9ba4kwoiWjjvqFC1fY5AeV",
                          "5J2KeFptc73WTZPoT1Sd59prFep6SobGobCYm7T5ZnBKtuW9RL9",
                          "5HryThsy6ySbkaiGK12r8kQ21vNdH81T5iifFEZNTe59wfPFvU9",
                          "5Ji4N7LSSv3MAVkM3Gw2kq8GT5uxZYNaZ3d3y2C4Ex1m7vshjBN",
                          "5HqSHfckRKmZLqqWW7p2iU18BYvyjxQs2sksRWhXMWXsNEtxPZU",
                          ])

if __name__ == '__main__':
    unittest.main()
