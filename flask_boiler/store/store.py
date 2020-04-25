from collections import defaultdict, UserDict
from typing import Tuple

from google.cloud.firestore_v1 import DocumentSnapshot

from flask_boiler.business_property_store import BPSchema, to_ref
from flask_boiler.attrs.attribute import ReferenceAttribute
from flask_boiler.models.base import Serializable
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj


reference = ReferenceAttribute


class Store(Serializable):

    _schema_base = BPSchema

    @classmethod
    def from_snapshot_struct(cls, snapshot_struct, **kwargs):
        struct, container = snapshot_struct.to_struct_and_container()
        store = cls(**kwargs)
        store.struct = struct
        store._container = container
        return store

    def add_snapshot(self, key, dm_cls, snapshot: DocumentSnapshot):
        struct_sub, container = self.struct, self._container
        if "." in "key":
            parent_name, key = key.split(".")
            struct_sub = struct_sub[parent_name]
        struct_sub[key] = (dm_cls, snapshot.reference.id)
        container.set(snapshot.reference._document_path, snapshot)

    def __init__(self, obj_options=None):
        """

        :param struct:
        :param snapshot_container:
        :param obj_options: keyword arguments to pass to snapshot_to_obj
            (eventually applied to obj_cls.from_dict)
        """
        super().__init__()
        if obj_options is None:
            obj_options = dict()
        self._obj_options = obj_options
        self._container = SnapshotContainer()
        self.struct = Struct(schema_obj=self.schema_obj)
        # self._info = self._get_manifests(self.struct, self.schema_obj)
        self.objs = dict()

    @property
    def _g(self):
        self._info = self._get_manifests(self.struct, self.schema_obj)
        return self._info[0]

    @property
    def _gr(self):
        self._info = self._get_manifests(self.struct, self.schema_obj)
        return self._info[1]

    @property
    def _manifest(self):
        self._info = self._get_manifests(self.struct, self.schema_obj)
        return self._info[2]

    @property
    def bprefs(self):
        return self._manifest.copy()

    def refresh(self):
        for doc_ref in self._manifest:
            self.objs[doc_ref] = snapshot_to_obj(
                self._container.get(doc_ref),
                super_cls=None,
                **self._obj_options
            )

    def __getattr__(self, item):

        if item not in self._g:
            raise AttributeError

        if isinstance(self._g[item], dict):
            return {
                k: self.objs[v]
                for k, v in self._g[item].items()
            }
        else:
            return self.objs[self._g[item]]

    def propagate_back(self):
        for _, obj in self.objs.items():
            obj.save()

    @staticmethod
    def _get_manifests(struct, schema_obj) -> Tuple:

        g, gr, manifest = dict(), defaultdict(list), set()

        for fd in schema_obj.structural_ref_fields:
            key = fd.attribute
            val = struct[key]

            if fd.many:
                g[key] = dict()
                for k, v in val.items():
                    if "." in k:
                        raise ValueError
                    doc_ref = to_ref(*v)
                    g[key][k] = doc_ref
                    gr[doc_ref].append("{}.{}".format(key, k))
                    manifest.add(doc_ref)
            else:
                doc_ref = to_ref(*val)
                g[key] = doc_ref
                gr[doc_ref].append(key)
                manifest.add(doc_ref)

        return dict(g), dict(gr), manifest

