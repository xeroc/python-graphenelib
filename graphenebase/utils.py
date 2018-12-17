# -*- coding: utf-8 -*-
import sys
import time
from datetime import datetime, timezone

timeFormat = "%Y-%m-%dT%H:%M:%S"


def _bytes(x):  # pragma: no branch
    """ Python3 and Python2 compatibility
    """
    if sys.version > "3":
        return bytes(x, "utf8")
    else:  # pragma: no cover
        return x.__bytes__()


def unicodify(data):
    r = []
    for s in data:
        o = ord(s)
        if (o <= 7) or (o == 11) or (o > 13 and o < 32):
            r.append("u%04x" % o)
        elif o == 8:
            r.append("b")
        elif o == 9:
            r.append("\t")
        elif o == 10:
            r.append("\n")
        elif o == 12:
            r.append("f")
        elif o == 13:
            r.append("\r")
        else:
            r.append(s)
    return bytes("".join(r), "utf-8")


def formatTime(t):
    """ Properly Format Time for permlinks
    """
    if isinstance(t, (float, int)):
        return datetime.utcfromtimestamp(t).strftime(timeFormat)
    elif isinstance(t, datetime):
        return t.strftime(timeFormat)
    else:
        raise ValueError("formatTime expects float/int, or datetime")


def formatTimeFromNow(secs=0):
    """ Properly Format Time that is `x` seconds in the future

        :param int secs: Seconds to go in the future (`x>0`) or the
                         past (`x<0`)
        :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
        :rtype: str

    """
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime(timeFormat)


def parse_time(block_time):
    """Take a string representation of time from the blockchain, and parse it
       into datetime object.
    """
    return datetime.strptime(block_time, timeFormat).replace(tzinfo=timezone.utc)


# Legacy names
formatTimeString = formatTime
