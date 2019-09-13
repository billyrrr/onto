import warnings
from typing import TypeVar

from google.cloud.firestore import DocumentReference
from google.cloud.firestore import Transaction, DocumentSnapshot

from flask_boiler.helpers import RelationshipReference
# from flask_boiler.view_model import ViewModel
from flask_boiler.collection_mixin import CollectionMixin
from flask_boiler.serializable import Serializable
from flask_boiler.factory import ClsFactory


class FirestoreObjectClsFactory(ClsFactory):
    pass


class FirestoreObjectMixin:

    @classmethod
    def create(cls, doc_ref=None):
        if doc_ref is None:
            raise ValueError
        obj = cls(doc_ref=doc_ref)
        return obj

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

    def save(self, transaction: Transaction = None):
        d = self._export_as_dict(to_save=True)
        if transaction is None:
            self.doc_ref.set(document_data=d)
        else:
            transaction.set(reference=self.doc_ref,
                            document_data=d)

    def delete(self, transaction: Transaction = None):
        if transaction is None:
            self.doc_ref.delete()
        else:
            transaction.delete(reference=self.doc_ref)


class FirestoreObject(FirestoreObjectMixin, Serializable, CollectionMixin):

    def __init__(self, doc_ref=None):
        super().__init__()
        self._doc_ref = doc_ref
        self.transaction = None

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

    def _import_val(self, val, to_get=False):

        def is_nested_relationship(val):
            return isinstance(val, RelationshipReference) and val.nested

        def is_ref_only_relationship(val):
            return isinstance(val, RelationshipReference) and not val.nested

        def nest_relationship(val: RelationshipReference):
            res = None
            if self.transaction is None:
                res = val.doc_ref.get().to_dict()
            else:
                res = val.doc_ref.get(transaction=self.transaction).to_dict()
            return res

        if is_nested_relationship(val):
            if to_get:
                return nest_relationship(val)
            else:
                return val.doc_ref
        elif is_ref_only_relationship(val):
            return val.doc_ref
        else:
            return super()._import_val(val)


T = TypeVar('T', covariant=True)


def snapshot_to_obj(
        snapshot: DocumentSnapshot,
        super_cls: T = None) -> T:
    """ Converts a firestore document snapshot to FirestoreObject

    :param snapshot: firestore document snapshot
    :param super_cls: subclass of FirestoreObject
    :return:
    """
    d = snapshot.to_dict()
    obj_type = d["obj_type"]
    obj_cls = super_cls.get_cls_from_name(obj_type)

    if obj_cls is None:
        raise ValueError("Cannot read obj_type: {}. "
                         "Make sure that obj_type is a subclass of {}. "
                         .format(obj_type, super_cls))

    if super_cls is not None:
        assert issubclass(obj_cls, super_cls)

    obj = obj_cls.create(doc_ref=snapshot.reference)
    obj._import_properties(d)
    return obj
