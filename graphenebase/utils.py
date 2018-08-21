import sys


def _bytes(x):  # pragma: no branch
    """ Python3 and Python2 compatibility
    """
    if sys.version > '3':
        return bytes(x, 'utf8')
    else:  # pragma: no cover
        # return bytes(x).encode('utf8')
        return x.__bytes__()


def unicodify(data):
    r = []
    for s in data:
        o = ord(s)
        if o <= 7:
            r.append("u%04x" % o)
        elif o == 8:
            r.append("b")
        elif o == 9:
            r.append("\t")
        elif o == 10:
            r.append("\n")
        elif o == 11:
            r.append("u%04x" % o)
        elif o == 12:
            r.append("f")
        elif o == 13:
            r.append("\r")
        elif o > 13 and o < 32:
            r.append("u%04x" % o)
        else:
            r.append(s)
    return bytes("".join(r), "utf-8")
