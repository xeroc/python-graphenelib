import warnings


class GrapheneClient():
    """ This class is **deprecated**. The old implementation can by
        found in python-bitshares (still deprecated, but functional)
    """

    def __init__(self, *args, **kwargs):
        raise DeprecationWarning(
            "[DeprecationWarning] The GrapheneClient is deprecated. The "
            "old implementation can be found in\n\n"
            "    from bitsharesdeprecated.client import BitSharesClient"
        )
        super(GrapheneClient, self).__init__(*args, **kwargs)
