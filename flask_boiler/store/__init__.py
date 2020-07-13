from collections import defaultdict
from typing import Tuple

from .gallery import Gallery
from .store import reference
# from .store import Store
from ..business_property_store import BPSchema, to_ref
from ..firestore_object import FirestoreObject, FirestoreObjectValMixin
from ..models.base import Serializable
from ..struct import Struct
from ..utils import snapshot_to_obj

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

class Store(FirestoreObjectValMixin, Serializable):

    _schema_base = BPSchema

    @classmethod
    def from_struct(cls, struct):
        return cls.from_dict(d=struct)

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

    @classmethod
    def _import_from_dict(cls, *args, **kwargs):
        _store = Gallery()
        obj = super()._import_from_dict(*args, **kwargs, _store=_store)
        _store.refresh(transaction=None)
        return obj

    def propagate_back(self):
        for _, obj in self.objs.items():
            obj.save()



