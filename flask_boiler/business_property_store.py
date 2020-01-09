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


class BusinessPropertyStore(Schemed):

    def __init__(self, struct):
        super().__init__()

        self._container = SnapshotContainer()
        self.struct = struct
        self._g, self._gr, self._manifest = \
            self._get_manifests(self.struct, self.schema_obj)

    def __getattr__(self, item):

        if isinstance(self._g[item], dict):
            return {
                k: snapshot_to_obj(self._container.get(v))
                for k, v in self._g[item].items()
            }
        else:
            return snapshot_to_obj(self._container.get(self._g[item]))

    @staticmethod
    def _get_manifests(struct, schema_obj) -> Tuple:

        g, gr, manifest = dict(), defaultdict(list), set()

        for fd in schema_obj.structural_ref_fields:
            key = fd.attribute
            val = struct[key]

            dm_cls = fd.dm_cls
            if fd.many:
                g[key] = dict()
                for k, v in val.items():
                    if "." in k:
                        raise ValueError
                    doc_ref = to_ref(dm_cls, v)
                    g[key][k] = doc_ref
                    gr[doc_ref].append("{}.{}".format(key, k))
                    manifest.add(doc_ref)
            else:
                doc_ref = to_ref(dm_cls, val)
                g[key] = doc_ref
                gr[doc_ref].append(key)
                manifest.add(doc_ref)

        return dict(g), dict(gr), manifest
