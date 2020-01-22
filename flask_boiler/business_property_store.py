from collections import defaultdict
from typing import Tuple

from google.cloud.firestore import DocumentReference

from flask_boiler.fields import StructuralRef
from flask_boiler.schema import Schema
from flask_boiler.serializable import Schemed
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.utils import snapshot_to_obj


def to_ref(dm_cls, dm_doc_id):
    """
    TODO: check doc_ref._document_path alternatives that are compatible
        with firestore listeners

    :param val:
    :return:
    """
    doc_ref: DocumentReference = dm_cls._get_collection().document(dm_doc_id)
    return doc_ref._document_path


class BPSchema(Schema):

    @property
    def structural_ref_fields(self):
        return [fd for _, fd in self.fields.items() if isinstance(fd, StructuralRef)]


class BusinessPropertyStore:

    def __init__(self, struct, snapshot_container):
        super().__init__()
        self._container = snapshot_container
        self.struct = struct
        self.schema_obj = struct.schema_obj
        self._g, self._gr, self._manifest = \
            self._get_manifests(self.struct, self.schema_obj)
        self.objs = dict()

    @property
    def bprefs(self):
        return self._manifest.copy()

    def refresh(self):
        for doc_ref in self._manifest:
            self.objs[doc_ref] = snapshot_to_obj(self._container.get(doc_ref))

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
