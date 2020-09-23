from collections import defaultdict

from onto.attrs.attribute import RelationshipAttribute
from onto.common import _NA
from typing import Tuple

from onto.mapper.fields import StructuralRef
from onto.mapper.schema import SchemaBase
from onto.utils import snapshot_to_obj
from onto.context import Context as CTX


def to_ref(dm_cls, dm_doc_id):
    """
    TODO: check doc_ref._document_path alternatives that are compatible
        with firestore listeners

    :param val:
    :return:
    """
    from onto.database.firestore import FirestoreReference

    doc_ref: FirestoreReference = dm_cls._get_collection() / dm_doc_id

    return CTX.db.make_document_path(doc_ref)


class BusinessPropertyStore:

    @classmethod
    def from_snapshot_struct(cls, snapshot_struct, **kwargs):
        struct, container = snapshot_struct.to_struct_and_container()
        store = BusinessPropertyStore(struct=struct,
                                      snapshot_container=container,
                                      **kwargs
                                      )
        store.refresh()
        return store

    def __init__(self, struct, snapshot_container, obj_options=None):
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
        self._container = snapshot_container
        self.struct = struct
        self.schema_obj = struct.schema_obj
        self._g, self._gr, self._manifest = \
            self._get_manifests(self.struct, self.schema_obj)
        self.objs = dict()

    @property
    def bprefs(self):
        return {doc_ref for (_, doc_ref) in self._manifest.copy()}

    def refresh(self):
        for obj_cls, doc_ref in self._manifest:
            self.objs[doc_ref] = snapshot_to_obj(
                self._container.get(doc_ref),
                super_cls=obj_cls,
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
            val = struct.get_item(key)

            if val is None:
                continue

            if fd.many:
                g[key] = dict()
                for k, v in val.items():
                    if "." in k:
                        raise ValueError
                    doc_ref = to_ref(*v)
                    g[key][k] = doc_ref
                    gr[doc_ref].append("{}.{}".format(key, k))
                    manifest.add( (v[0], doc_ref) )
            else:
                doc_ref = to_ref(*val)
                g[key] = doc_ref
                gr[doc_ref].append(key)
                manifest.add( (val[0], doc_ref) )

        return dict(g), dict(gr), manifest

