import json
import lzma
from graphenebase.base58 import base58encode, base58decode
from binascii import hexlify, unhexlify

invoice = {
    "to": "bitshareseurope",
    "to_label": "BitShares Europre",
    "currency": "EUR",
    "memo": "Invoice #1234",
    "line_items": [
        {"label": "Something to Buy", "quantity": 1, "price": "10.00"},
        {"label": "10 things to Buy", "quantity": 10, "price": "1.00"}
    ],
    "note": "Payment for reading awesome documentation",
    "callback": "https://bitshares.eu/complete"
}

compressed = lzma.compress(bytes(json.dumps(invoice), 'utf-8'), format=lzma.FORMAT_ALONE)
b58 = base58encode(hexlify(compressed).decode('utf-8'))
url = "https://bitshares.openledger.info/#/invoice/%s" % b58

print(url)
