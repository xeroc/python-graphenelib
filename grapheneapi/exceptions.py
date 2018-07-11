class HttpInvalidStatusCode(Exception):
    pass


class RPCError(Exception):
    pass


class NumRetriesReached(Exception):
    pass


class RPCRequestError(Exception):
    pass
