# -*- coding: utf-8 -*-
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


def getOperationNameForId(i: int):
    """ Convert an operation id into the corresponding string
    """
    assert isinstance(i, (int)), "This method expects an integer argument"
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    raise ValueError("Unknown Operation ID %d" % i)


def getOperationName(id: str):
    """ This method returns the name representation of an operation given
        its value as used in the API
    """
    if isinstance(id, str):
        # Some graphene chains (e.g. steem) do not encode the
        # operation_type as id but in its string form
        assert id in operations.keys(), "Unknown operation {}".format(id)
        return id
    elif isinstance(id, int):
        return getOperationNameForId(id)
    else:
        raise ValueError
