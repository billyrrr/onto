import warnings

from google.cloud.firestore import DocumentReference
from google.cloud.firestore import Transaction

from flask_boiler.helpers import RelationshipReference, EmbeddedElement
# from flask_boiler.view_model import ViewModel
from flask_boiler.collection_mixin import CollectionMixin
from flask_boiler.serializable import Serializable
from flask_boiler.factory import ClsFactory
from flask_boiler.utils import snapshot_to_obj


class FirestoreObjectMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_firestore_ref(self):
        warnings.warn("Please use .doc_ref instead. ", DeprecationWarning)
        return self.doc_ref

    @property
    def doc_ref(self) -> DocumentReference:
        """
        Must be implemented in subclass
        """
        raise NotImplementedError

    @property
    def doc_ref_str(self):
        """
        Used for serializing the object
        """
        return self.doc_ref.path

    @classmethod
    def get(cls, *, doc_ref=None, transaction=None, **kwargs):
        if transaction is None:
            snapshot = doc_ref.get()
        else:
            snapshot = doc_ref.get(transaction=transaction)
        obj = snapshot_to_obj(snapshot=snapshot, super_cls=cls)
        return obj

    @classmethod
    def from_snapshot(cls, snapshot=None):
        obj = snapshot_to_obj(snapshot=snapshot, super_cls=cls)
        return obj

    def save(self, transaction: Transaction = None, doc_ref=None, save_rel=True):
        if doc_ref is None:
            doc_ref = self.doc_ref

        d = self._export_as_dict(to_save=save_rel)

        if transaction is None:
            doc_ref.set(document_data=d)
        else:
            transaction.set(reference=doc_ref,
                            document_data=d)

    def delete(self, transaction: Transaction = None):
        if transaction is None:
            self.doc_ref.delete()
        else:
            transaction.delete(reference=self.doc_ref)


class FirestoreObjectValMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _export_val(self, val, to_save=False):

        def is_nested_relationship(val):
            return isinstance(val, RelationshipReference) and val.nested

        def is_ref_only_relationship(val):
            return isinstance(val, RelationshipReference) and not val.nested

        def nest_relationship(obj):
            if self.transaction is None:
                obj.save()
            else:
                obj.save(transaction=self.transaction)
            return obj.doc_ref

        if is_nested_relationship(val):
            if to_save:
                return nest_relationship(val.obj)
            else:
                return val.obj.doc_ref
        elif is_ref_only_relationship(val):
            return val.doc_ref

        else:
            return super()._export_val(val, to_save=to_save)

    def _export_val_view(self, val):

        def get_vm(doc_ref):
            obj = FirestoreObject.get(doc_ref=doc_ref,
                                      transaction=self.transaction)
            return obj._export_as_view_dict()

        if isinstance(val, RelationshipReference):
            if val.obj is not None:
                return val.obj._export_as_view_dict()
            elif val.doc_ref is not None:
                return get_vm(val.doc_ref)
            else:
                return val.doc_ref
        else:
            return super()._export_val_view(val)

    @classmethod
    def _import_val(cls, val, to_get=False, must_get=False, transaction=None):

        def is_nested_relationship(val):
            return isinstance(val, RelationshipReference) and val.nested

        def is_ref_only_relationship(val):
            return isinstance(val, RelationshipReference) and not val.nested

        def nest_relationship(val: RelationshipReference):
            if transaction is None:
                snapshot = val.doc_ref.get()
                return snapshot_to_obj(snapshot)
            else:
                snapshot = val.doc_ref.get(transaction=transaction)
                return snapshot_to_obj(snapshot, transaction=transaction)

        if is_nested_relationship(val):
            if to_get:
                return nest_relationship(val)
            else:
                return val.doc_ref
        elif is_ref_only_relationship(val):
            if must_get:
                return nest_relationship(val)
            else:
                return val.doc_ref
        else:
            return super()._import_val(
                val, to_get=to_get, transaction=transaction)


class FirestoreObject(FirestoreObjectValMixin,
                      FirestoreObjectMixin,
                      Serializable,
                      CollectionMixin):

    def __init__(self, *args, doc_ref=None, transaction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._doc_ref = doc_ref
        self.transaction = transaction
