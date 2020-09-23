from onto.mapper.fields import StructuralRef
from onto.mapper.schema import SchemaBase
from onto.firestore_object import FirestoreObjectValMixin
from onto.models.base import Serializable
from onto.store.struct import struct_ref

"""
Store provides a unified interface to access dependencies from a View Model
Shelf provides a key-value store with reference as key and instance of 
    Domain Model as value (single moment in time) 
Snapshot Container stores snapshots and manages versions of the snapshots 
    (all moment in time) 

The same reference and snapshot may map to different obj_type. 
Thus shelf layer keeps obj_type and reference as key, and 
    objects as values. 
"""


class BPSchema(SchemaBase):

    @classmethod
    def from_dict(cls, fields, name):
        for _, val in fields.items():
            if not issubclass(val.__class__, StructuralRef):
                raise TypeError
        return super().from_dict(fields=fields, name=name)

    @property
    def structural_ref_fields(self):
        return [fd for _, fd in self.fields.items() if isinstance(fd, StructuralRef)]


class Store(FirestoreObjectValMixin, Serializable):
    class Meta:
        case_conversion = False

    _schema_base = BPSchema

    @classmethod
    def from_struct(cls, struct):
        from onto.store import Gallery

        schema_obj = cls.get_schema_obj()
        d = schema_obj.load(struct)
        _store = Gallery()
        d = cls._import_from_dict(d, _store=_store, transaction=None)
        _store.refresh(transaction=None)
        instance = cls.new(**d)  # TODO: fix unexpected arguments
        return instance

    @classmethod
    def from_objects(cls, **kwargs):
        d = {
            key: struct_ref(obj=val)
            for key, val in kwargs.items()
        }
        return cls.from_struct(d)

    @classmethod
    def from_snapshot_struct(cls, snapshot_struct, **kwargs):
        struct, container = snapshot_struct.to_struct_and_container()
        store = cls(**kwargs)
        store.struct = struct
        store._container = container
        return store

    # def add_snapshot(self, key, dm_cls, snapshot: DocumentSnapshot):
    #     struct_sub, container = self.struct, self._container
    #     if "." in "key":
    #         parent_name, key = key.split(".")
    #         struct_sub = struct_sub[parent_name]
    #     struct_sub[key] = (dm_cls, snapshot.reference.id)
    #     container.set(snapshot.reference._document_path, snapshot)

    def __init__(
            self, *args, readonly=False, transaction=None, _store=None,
            **kwargs):
        self.transaction = transaction
        self.readonly = readonly
        super().__init__(*args, **kwargs)

    # def __init__(self, obj_options=None, **kwargs):
    #     """
    #
    #     :param struct:
    #     :param snapshot_container:
    #     :param obj_options: keyword arguments to pass to snapshot_to_obj
    #         (eventually applied to obj_cls.from_dict)
    #     """
    #     super().__init__(**kwargs)
    #     if obj_options is None:
    #         obj_options = dict()
    #     self._obj_options = obj_options
    #     self._gallery = Gallery()
    #     self.struct = Struct(schema_obj=self.schema_obj)
    #     # self._info = self._get_manifests(self.struct, self.schema_obj)
    #     self.objs = dict()

    def propagate_back(self):
        """
        TODO: add transaction
        :return:
        """
        self._export_as_dict(_store=self._store, transaction=None)
        self._store.save()
