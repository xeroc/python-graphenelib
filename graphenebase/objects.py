# -*- coding: utf-8 -*-
import json

from collections import OrderedDict
from graphenebase.types import (
    Uint8,
    Int16,
    Uint16,
    Uint32,
    Uint64,
    Varint32,
    Int64,
    String,
    Bytes,
    Void,
    Array,
    PointInTime,
    Signature,
    Bool,
    Set,
    Fixed_array,
    Optional,
    Static_variant,
    Map,
    Id,
    VoteId,
    ObjectId,
    JsonObj,
)
from .chains import known_chains
from .objecttypes import object_type
from .account import PublicKey
from .chains import default_prefix
from .operationids import operations


class Operation(list):
    """ The superclass for an operation. This class i used to instanciate an
        operation, identify the operationid/name and serialize the operation
        into bytes.
    """

    module = "graphenebase.operations"
    fromlist = ["operations"]
    operations = operations

    def __init__(self, op, **kwargs):
        list.__init__(self, [0, GrapheneObject()])

        # Are we dealing with an actual operation as list of opid and payload?
        if isinstance(op, list) and len(op) == 2:
            self._setidanename(op[0])
            self.set(**op[1])

        # Here, we allow to only load the Operation as Template without data
        elif isinstance(op, str) or isinstance(op, int):
            self._setidanename(op)
            if kwargs:
                self.set(**kwargs)

        elif isinstance(op, GrapheneObject):
            self._loadGrapheneObject(op)

        else:
            raise ValueError("Unknown format for Operation({})".format(type(op)))

    @property
    def id(self):
        return self[0]

    @id.setter
    def id(self, value):
        assert isinstance(value, int)
        self[0] = value

    @property
    def operation(self):
        return self[1]

    @operation.setter
    def operation(self, value):
        assert isinstance(value, dict)
        self[1] = value

    @property
    def op(self):
        return self[1]

    def set(self, **data):
        try:
            klass = self.klass()
        except Exception:  # pragma: no cover
            raise NotImplementedError("Unimplemented Operation %s" % self.name)
        self.operation = klass(**data)

    def _setidanename(self, identifier):
        if isinstance(identifier, int):
            self.id = int(identifier)
            self.name = self.getOperationNameForId(self.id)
        else:
            assert identifier in self.ops
            self.id = self.getOperationIdForName(identifier)
            self.name = identifier

    @property
    def opId(self):
        return self.id

    @property
    def klass_name(self):
        return self.name[0].upper() + self.name[1:]  # klassname

    def _loadGrapheneObject(self, op):
        assert isinstance(op, GrapheneObject)
        self.operation = op
        self.name = op.__class__.__name__.lower()
        self.id = self.getOperationIdForName(self.name)

    def __bytes__(self):
        return bytes(Id(self.id)) + bytes(self.op)

    def __str__(self):
        return json.dumps(self.__json__())

    def __json__(self):
        return [self.id, self.op.json()]

    def _getklass(self, name):
        module = __import__(self.module, fromlist=self.fromlist)
        class_ = getattr(module, name)
        return class_

    def klass(self):
        return self._getklass(self.klass_name)

    @property
    def ops(self):
        if callable(self.operations):  # pragma: no cover
            # Legacy support
            return self.operations()
        else:
            return self.operations

    def getOperationIdForName(self, name):
        return self.ops[name]

    def getOperationNameForId(self, i):
        """ Convert an operation id into the corresponding string
        """
        for key in self.ops:
            if int(self.ops[key]) is int(i):
                return key
        raise ValueError("Unknown Operation ID %d" % i)

    toJson = __json__
    json = __json__


class GrapheneObject(OrderedDict):
    """ Core abstraction class

        This class is used for any JSON reflected object in Graphene.

        * ``instance.__json__()``: encodes data into json format
        * ``bytes(instance)``: encodes data into wire format
        * ``str(instances)``: dumps json object as string

    """

    def __init__(self, *args, **kwargs):

        if len(args) == 1 and isinstance(args[0], self.__class__):
            # In this case, there is only one argument which is already an
            # instance of a class that inherits Graphene Object, hence, we copy
            # data and are done
            # This basic allows to do
            #
            #    Asset(Asset(amount=1, asset_id="1.3.0"))
            self.data = args[0].data.copy()
            return

        if len(args) == 1 and isinstance(args[0], (dict, OrderedDict)):
            if hasattr(self, "detail"):
                super().__init__(self.detail(**args[0]))
            else:
                OrderedDict.__init__(self, args[0])
            return

        elif kwargs and hasattr(self, "detail"):
            # If I receive kwargs, I need detail() implemented!
            super().__init__(self.detail(*args, **kwargs))

    def __bytes__(self):
        if len(self) == 0:
            return bytes()
        b = b""
        for name, value in self.items():
            if isinstance(value, str):
                b += bytes(value, "utf-8")
            else:
                b += bytes(value)
        return b

    def __json__(self):
        if len(self) == 0:
            return {}
        d = {}  # JSON output is *not* ordered
        for name, value in self.items():
            if isinstance(value, Optional) and value.isempty():  # pragma: no cover
                continue

            if isinstance(value, String):
                d.update({name: str(value)})
            else:
                try:
                    d.update({name: JsonObj(value)})
                except Exception:
                    d.update({name: value.__str__()})
        return d

    def __str__(self):
        return json.dumps(self.__json__())

    # Legacy support
    @property
    def data(self):  # pragma: no cover
        """ Read data explicitly (backwards compatibility)
        """
        return self

    @data.setter
    def data(self, data):  # pragma: no cover
        """ Set data through a setter (backwards compatibility)
        """
        self.update(data)

    toJson = __json__
    json = __json__


# Legacy
def isArgsThisClass(self, args):
    return len(args) == 1 and type(args[0]).__name__ == type(self).__name__


# Common Objects
class Asset(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("amount", Int64(kwargs["amount"])),
                ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
            ]
        )
