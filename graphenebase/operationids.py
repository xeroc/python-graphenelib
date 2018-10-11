#: Operation ids
ops = [
    "demooepration",
    "newdemooepration",
    "newdemooepration2",
    "nonexisting2",
    "nonexisting3",
    "account_create",
]
operations = {o: ops.index(o) for o in ops}


def getOperationNameForId(i):
    """ Convert an operation id into the corresponding string
    """
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    raise ValueError("Unknown Operation ID %d" % i)
