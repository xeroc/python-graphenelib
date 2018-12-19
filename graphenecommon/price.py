# -*- coding: utf-8 -*-
from fractions import Fraction
from .exceptions import InvalidAssetException
from .utils import assets_from_string, formatTimeString, parse_time
from .instance import AbstractBlockchainInstanceProvider


class Price(dict, AbstractBlockchainInstanceProvider):
    """ This class deals with all sorts of prices of any pair of assets to
        simplify dealing with the tuple::

            (quote, base)

        each being an instance of :class:`.amount.Amount`. The
        amount themselves define the price.

        .. note::

            The price (floating) is derived as ``base/quote``

        :param list args: Allows to deal with different representations of a price
        :param asset.Asset base: Base asset
        :param asset.Asset quote: Quote asset
        :param instance blockchain_instance: instance to use when accesing a RPC
        :returns: All data required to represent a price
        :rtype: dict

        Way to obtain a proper instance:

            * ``args`` is a str with a price and two assets
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of :class:`.asset.Asset`
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of ``str``
            * ``args`` can be dict with keys ``price``, ``base``, and ``quote`` (*graphene balances*)
            * ``args`` can be dict with keys ``base`` and ``quote``
            * ``args`` can be dict with key ``receives`` (filled orders)
            * ``args`` being a list of ``[quote, base]`` both being instances of :class:`.amount.Amount`
            * ``args`` being a list of ``[quote, base]`` both being instances of ``str`` (``amount symbol``)
            * ``base`` and ``quote`` being instances of :class:`.asset.Amount`

        This allows instanciations like:

        * ``Price("0.315 USD/BTS")``
        * ``Price(0.315, base="USD", quote="BTS")``
        * ``Price(0.315, base=self.asset_class("USD"), quote=self.asset_class("BTS"))``
        * ``Price({"base": {"amount": 1, "asset_id": "1.3.0"}, "quote": {"amount": 10, "asset_id": "1.3.106"}})``
        * ``Price({"receives": {"amount": 1, "asset_id": "1.3.0"}, "pays": {"amount": 10, "asset_id": "1.3.106"}}, base_asset=self.asset_class("1.3.0"))``
        * ``Price(quote="10 GOLD", base="1 USD")``
        * ``Price("10 GOLD", "1 USD")``
        * ``Price(self.amount_class("10 GOLD"), self.amount_class("1 USD"))``
        * ``Price(1.0, "USD/GOLD")``

        Instances of this class can be used in regular mathematical expressions
        (``+-*/%``) such as:

        .. code-block:: python

            >>> from bitshares.price import Price
            >>> Price("0.3314 USD/BTS") * 2
            0.662600000 USD/BTS

    """

    def __init__(
        self,
        *args,
        base=None,
        quote=None,
        base_asset=None,  # to identify sell/buy
        **kwargs
    ):
        self.define_classes()
        assert self.amount_class
        assert self.asset_class

        if len(args) == 1 and isinstance(args[0], str) and not base and not quote:
            import re

            price, assets = args[0].split(" ")
            base_symbol, quote_symbol = assets_from_string(assets)
            base = self.asset_class(base_symbol, blockchain_instance=self.blockchain)
            quote = self.asset_class(quote_symbol, blockchain_instance=self.blockchain)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = self.amount_class(
                amount=frac.denominator,
                asset=quote,
                blockchain_instance=self.blockchain,
            )
            self["base"] = self.amount_class(
                amount=frac.numerator, asset=base, blockchain_instance=self.blockchain
            )

        elif (
            len(args) == 1
            and isinstance(args[0], dict)
            and "base" in args[0]
            and "quote" in args[0]
        ):
            assert "price" not in args[0], "You cannot provide a 'price' this way"
            # Regular 'price' objects according to the backend
            base_id = args[0]["base"]["asset_id"]
            if args[0]["base"]["asset_id"] == base_id:
                self["base"] = self.amount_class(
                    args[0]["base"], blockchain_instance=self.blockchain
                )
                self["quote"] = self.amount_class(
                    args[0]["quote"], blockchain_instance=self.blockchain
                )
            else:
                self["quote"] = self.amount_class(
                    args[0]["base"], blockchain_instance=self.blockchain
                )
                self["base"] = self.amount_class(
                    args[0]["quote"], blockchain_instance=self.blockchain
                )

        elif len(args) == 1 and isinstance(args[0], dict) and "receives" in args[0]:
            # Filled order
            assert base_asset, "Need a 'base_asset' asset"
            base_asset = self.asset_class(
                base_asset, blockchain_instance=self.blockchain
            )
            if args[0]["receives"]["asset_id"] == base_asset["id"]:
                # If the seller received "base" in a quote_base market, than
                # it has been a sell order of quote
                self["base"] = self.amount_class(
                    args[0]["receives"], blockchain_instance=self.blockchain
                )
                self["quote"] = self.amount_class(
                    args[0]["pays"], blockchain_instance=self.blockchain
                )
                self["type"] = "sell"
            else:
                # buy order
                self["base"] = self.amount_class(
                    args[0]["pays"], blockchain_instance=self.blockchain
                )
                self["quote"] = self.amount_class(
                    args[0]["receives"], blockchain_instance=self.blockchain
                )
                self["type"] = "buy"

        elif len(args) == 1 and (
            isinstance(base, self.asset_class) and isinstance(quote, self.asset_class)
        ):
            price = args[0]
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = self.amount_class(
                amount=frac.denominator,
                asset=quote,
                blockchain_instance=self.blockchain,
            )
            self["base"] = self.amount_class(
                amount=frac.numerator, asset=base, blockchain_instance=self.blockchain
            )

        elif len(args) == 1 and (
            isinstance(base, self.amount_class) and isinstance(quote, self.amount_class)
        ):
            price = args[0]
            self["quote"] = quote
            self["base"] = base

        elif len(args) == 1 and isinstance(base, str) and isinstance(quote, str):
            price = args[0]
            base = self.asset_class(base, blockchain_instance=self.blockchain)
            quote = self.asset_class(quote, blockchain_instance=self.blockchain)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = self.amount_class(
                amount=frac.denominator,
                asset=quote,
                blockchain_instance=self.blockchain,
            )
            self["base"] = self.amount_class(
                amount=frac.numerator, asset=base, blockchain_instance=self.blockchain
            )

        elif len(args) == 0 and isinstance(base, str) and isinstance(quote, str):
            self["quote"] = self.amount_class(
                quote, blockchain_instance=self.blockchain
            )
            self["base"] = self.amount_class(base, blockchain_instance=self.blockchain)

        # len(args) > 1
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self["base"] = self.amount_class(
                args[1], blockchain_instance=self.blockchain
            )
            self["quote"] = self.amount_class(
                args[0], blockchain_instance=self.blockchain
            )

        elif (
            len(args) == 2
            and isinstance(args[0], self.amount_class)
            and isinstance(args[1], self.amount_class)
        ):
            self["quote"], self["base"] = args[0], args[1]

        # len(args) == 0
        elif isinstance(base, self.amount_class) and isinstance(
            quote, self.amount_class
        ):
            self["quote"] = quote
            self["base"] = base

        elif (
            len(args) == 2
            and (isinstance(args[0], float) or isinstance(args[0], int))
            and isinstance(args[1], str)
        ):
            import re

            price = args[0]
            base_symbol, quote_symbol = assets_from_string(args[1])
            base = self.asset_class(base_symbol, blockchain_instance=self.blockchain)
            quote = self.asset_class(quote_symbol, blockchain_instance=self.blockchain)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = self.amount_class(
                amount=frac.denominator,
                asset=quote,
                blockchain_instance=self.blockchain,
            )
            self["base"] = self.amount_class(
                amount=frac.numerator, asset=base, blockchain_instance=self.blockchain
            )

        else:
            raise ValueError("Couldn't parse 'Price'.")

    def __setitem__(self, key, value):
        """ Here we set "price" if we change quote or base
        """
        dict.__setitem__(self, key, value)
        if (
            "quote" in self and "base" in self and self["base"] and self["quote"]
        ):  # don't derive price for deleted Orders
            dict.__setitem__(
                self,
                "price",
                self._safedivide(self["base"]["amount"], self["quote"]["amount"]),
            )

    def copy(self):
        return self.__class__(base=self["base"].copy(), quote=self["quote"].copy())

    def _safedivide(self, a, b):
        if b != 0.0:
            return a / b
        else:
            return float("Inf")

    def symbols(self):
        return self["base"]["symbol"], self["quote"]["symbol"]

    def as_base(self, base):
        """ Returns the price instance so that the base asset is ``base``.

            Note: This makes a copy of the object!
        """
        if base == self["base"]["symbol"]:
            return self.copy()
        elif base == self["quote"]["symbol"]:
            return self.copy().invert()
        else:
            raise InvalidAssetException

    def as_quote(self, quote):
        """ Returns the price instance so that the quote asset is ``quote``.

            Note: This makes a copy of the object!
        """
        if quote == self["quote"]["symbol"]:
            return self.copy()
        elif quote == self["base"]["symbol"]:
            return self.copy().invert()
        else:
            raise InvalidAssetException

    def invert(self):
        """ Invert the price (e.g. go from ``USD/BTS`` into ``BTS/USD``)
        """
        tmp = self["quote"]
        self["quote"] = self["base"]
        self["base"] = tmp
        if "for_sale" in self and self["for_sale"]:
            self["for_sale"] = self.amount_class(
                self["for_sale"]["amount"] * self["price"], self["base"]["symbol"]
            )
        return self

    def json(self):
        """
        return {
            "base": self["base"].json(),
            "quote": self["quote"].json()
        }
        """
        quote = self["quote"]
        base = self["base"]
        frac = Fraction(int(quote) / int(base)).limit_denominator(
            10 ** base["asset"]["precision"]
        )
        return {
            "base": {"amount": int(frac.denominator), "asset_id": base["asset"]["id"]},
            "quote": {"amount": int(frac.numerator), "asset_id": quote["asset"]["id"]},
        }

    def __repr__(self):
        return "{price:.{precision}f} {base}/{quote}".format(
            price=self["price"],
            base=self["base"]["symbol"],
            quote=self["quote"]["symbol"],
            precision=(
                self["base"]["asset"]["precision"] + self["quote"]["asset"]["precision"]
            ),
        )

    def __float__(self):
        return self["price"]

    def __mul__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            # Rotate/invert other
            if (
                self["quote"]["symbol"] not in other.symbols()
                and self["base"]["symbol"] not in other.symbols()
            ):
                raise InvalidAssetException

            # base/quote = a/b
            # a/b * b/c = a/c
            a = self.copy()
            if self["quote"]["symbol"] == other["base"]["symbol"]:
                a["base"] = self.amount_class(
                    float(self["base"]) * float(other["base"]),
                    self["base"]["symbol"],
                    blockchain_instance=self.blockchain,
                )
                a["quote"] = self.amount_class(
                    float(self["quote"]) * float(other["quote"]),
                    other["quote"]["symbol"],
                    blockchain_instance=self.blockchain,
                )
            # a/b * c/a =  c/b
            elif self["base"]["symbol"] == other["quote"]["symbol"]:
                a["base"] = self.amount_class(
                    float(self["base"]) * float(other["base"]),
                    other["base"]["symbol"],
                    blockchain_instance=self.blockchain,
                )
                a["quote"] = self.amount_class(
                    float(self["quote"]) * float(other["quote"]),
                    self["quote"]["symbol"],
                    blockchain_instance=self.blockchain,
                )
            else:
                raise ValueError("Wrong rotation of prices")
        elif isinstance(other, self.amount_class):
            assert other["asset"]["id"] == self["quote"]["asset"]["id"]
            a = other.copy() * self["price"]
            a["asset"] = self["base"]["asset"].copy()
            a["symbol"] = self["base"]["asset"]["symbol"]
        else:
            a["base"] *= other
        return a

    def __imul__(self, other):
        if isinstance(other, Price):
            tmp = self * other
            self["base"] = tmp["base"]
            self["quote"] = tmp["quote"]
        else:
            self["base"] *= other
        return self

    def __div__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            # Rotate/invert other
            if sorted(self.symbols()) == sorted(other.symbols()):
                return float(self.as_base(self["base"]["symbol"])) / float(
                    other.as_base(self["base"]["symbol"])
                )
            elif self["quote"]["symbol"] in other.symbols():
                other = other.as_base(self["quote"]["symbol"])
            elif self["base"]["symbol"] in other.symbols():
                other = other.as_base(self["base"]["symbol"])
            else:
                raise InvalidAssetException
            a["base"] = self.amount_class(
                float(self["quote"] / other["quote"]),
                other["quote"]["symbol"],
                blockchain_instance=self.blockchain,
            )
            a["quote"] = self.amount_class(
                float(self["base"] / other["base"]),
                self["quote"]["symbol"],
                blockchain_instance=self.blockchain,
            )
        elif isinstance(other, self.amount_class):
            assert other["asset"]["id"] == self["quote"]["asset"]["id"]
            a = other.copy() / self["price"]
            a["asset"] = self["base"]["asset"].copy()
            a["symbol"] = self["base"]["asset"]["symbol"]
        else:
            a["base"] /= other
        return a

    def __idiv__(self, other):
        if isinstance(other, Price):
            tmp = self / other
            self["base"] = tmp["base"]
            self["quote"] = tmp["quote"]
        else:
            self["base"] /= other
        return self

    def __floordiv__(self, other):
        raise NotImplementedError("This is not possible as the price is a ratio")

    def __ifloordiv__(self, other):
        raise NotImplementedError("This is not possible as the price is a ratio")

    def __lt__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] < other["price"]
        else:
            return self["price"] < float(other or 0)

    def __le__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] <= other["price"]
        else:
            return self["price"] <= float(other or 0)

    def __eq__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] == other["price"]
        else:
            return self["price"] == float(other or 0)

    def __ne__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] != other["price"]
        else:
            return self["price"] != float(other or 0)

    def __ge__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] >= other["price"]
        else:
            return self["price"] >= float(other or 0)

    def __gt__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["quote"]["symbol"]
            return self["price"] > other["price"]
        else:
            return self["price"] > float(other or 0)

    __truediv__ = __div__
    __truemul__ = __mul__
    __str__ = __repr__
