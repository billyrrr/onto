from collections import UserDict, namedtuple
from onto.store.snapshot_container import SnapshotContainer

struct_ref = namedtuple(
    'struct_ref', ['dm_cls', 'id', 'ref', 'snapshot', 'obj'],
    defaults=[None, None, None, None, None])


class Struct(UserDict):

    def __init__(self, schema_obj=None, schema_cls=None):
        super().__init__()
        if schema_obj is None:
            schema_obj = schema_cls()
        self.schema_obj = schema_obj

    @property
    def vals(self):
        for _, val in self.data.items():
            if isinstance(val, dict):
                for _, v in val.items():
                    yield v
            else:
                yield val

    def get_item(self, key):
        """ Only return when key is defined. Used to access values of
        this object.

        :param key:
        :return:
        """
        if key not in self.data.keys():
            return None
        else:
            return self.data[key]

    def __getitem__(self, key):
        """
        Initializes a field to dict if it was not declared before

        :param item:
        :return:
        """

        if key not in self.data.keys():
            self.data[key] = dict()
        return super().__getitem__(key)


class SnapshotStruct(UserDict):

    def __init__(self, schema_obj=None, schema_cls=None):
        super().__init__()
        if schema_obj is None:
            schema_obj = schema_cls()
        self.schema_obj = schema_obj

    @property
    def vals(self):
        for _, val in self.data.items():
            if isinstance(val, dict):
                for _, v in val.items():
                    yield v
            else:
                yield val

    def __getitem__(self, key):
        """
        Initializes a field to dict if it was not declared before
        Used to write to this object.

        :param item:
        :return:
        """

        if key not in self.data.keys():
            self.data[key] = dict()
        return super().__getitem__(key)

    def to_struct_and_container(self):
        container = SnapshotContainer()
        struct = Struct(schema_obj=self.schema_obj)
        for key, val in self.data.items():
            if isinstance(val, dict):
                for k, v in val.items():
                    _cls, snapshot = v
                    struct[key][k] = (_cls, snapshot.reference.id)
                    container.set(snapshot.reference._document_path, snapshot)
            else:
                _cls, snapshot = val
                struct[key] = (_cls, snapshot.reference.id)
                container.set(snapshot.reference._document_path, snapshot)
        return struct, container
