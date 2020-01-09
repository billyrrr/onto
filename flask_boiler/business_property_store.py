from collections import defaultdict
from typing import Tuple

from google.cloud.firestore import DocumentReference

from flask_boiler.schema import Schema
from flask_boiler.serializable import Schemed
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.utils import snapshot_to_obj


def to_ref(val):
    """
    TODO: check doc_ref._document_path alternatives that are compatible
        with firestore listeners

    :param val:
    :return:
    """
    dm_cls, dm_doc_id = val
    doc_ref: DocumentReference = dm_cls._get_collection().document(dm_doc_id)
    return doc_ref._document_path


class BusinessPropertyStore:

    def __init__(self, struct):
        self._container = SnapshotContainer()
        self.struct = struct
        self._g, self._gr, self._manifest = self._get_manifests(struct)

    def __getattr__(self, item):

        if isinstance(self._g[item], dict):
            return {
                k: snapshot_to_obj(self._container.get(v))
                for k, v in self._g[item].items()
            }
        else:
            return snapshot_to_obj(self._container.get(self._g[item]))

    @staticmethod
    def _get_manifests(struct) -> Tuple:

        g, gr, manifest = dict(), defaultdict(list), set()

        for key, val in struct.items():
            if "." in key:
                raise ValueError
            if isinstance(val, dict):
                g[key] = dict()
                for k, v in val.items():
                    doc_ref = to_ref(v)
                    g[key][k] = doc_ref
                    gr[doc_ref].append("{}.{}".format(key, k))
                    manifest.add(doc_ref)
            else:
                doc_ref = to_ref(val)
                g[key] = doc_ref
                gr[doc_ref].append(key)
                manifest.add(doc_ref)

        return dict(g), dict(gr), manifest
