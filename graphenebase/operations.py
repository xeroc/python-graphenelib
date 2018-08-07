from collections import OrderedDict
import json
from .types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId, ObjectId,
)
from .objects import GrapheneObject, isArgsThisClass
from .account import PublicKey
from .chains import default_prefix
from .objects import Operation
from .operationids import operations


# Old style of defining an operation
class Demooepration(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('string', String(kwargs["string"])),
                ('extensions', Set([])),
            ]))


# New style of defining operation
class Newdemooepration(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict([
            ('string', String(kwargs["string"])),
            ('optional', Optional(String(kwargs.get("optional")))),
            ('extensions', Set([])),
        ])
