from collections import OrderedDict
from binascii import hexlify, unhexlify
from calendar import timegm
from datetime import datetime
import json
import struct
import time

from .account import PublicKey
from .chains import known_chains
from .types import *
from .signedtransactions import Signed_Transaction
from .operations import *
from .objects import *

timeformat = '%Y-%m-%dT%H:%M:%S%Z'

"""
    Auxiliary Calls
"""


def addRequiredFees(ws, ops, asset_id) :
    """ Auxiliary method to obtain the required fees for a set of
        operations. Requires a websocket connection to a witness node!
    """
    fees = ws.get_required_fees([JsonObj(i) for i in ops], asset_id)
    for i, d in enumerate(ops) :
        ops[i].op.data["fee"] = Asset(
            amount=fees[i]["amount"],
            asset_id=fees[i]["asset_id"]
        )
    return ops


def getBlockParams(ws) :
    """ Auxiliary method to obtain ``ref_block_num`` and
        ``ref_block_prefix``. Requires a websocket connection to a
        witness node!
    """
    dynBCParams = ws.get_dynamic_global_properties()
    ref_block_num = dynBCParams["head_block_number"] & 0xFFFF
    ref_block_prefix = struct.unpack_from("<I", unhexlify(dynBCParams["head_block_id"]), 4)[0]
    return ref_block_num, ref_block_prefix


def formatTimeFromNow(secs=0) :
    """ Properly Format Time that is `x` seconds in the future

     :param int secs: Seconds to go in the future (`x>0`) or the past (`x<0`)
     :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
     :rtype: str

    """
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime(timeformat)
