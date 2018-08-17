import sys


def _bytes(x):  # pragma: no branch
    """ Python3 and Python2 compatibility
    """
    if sys.version > '3':
        return bytes(x, 'utf8')
    else:
        # return bytes(x).encode('utf8')
        return x.__bytes__()
