import warnings

from google.cloud.firestore import DocumentReference
from google.cloud.firestore import Transaction

from flask_boiler import fields
from flask_boiler.helpers import RelationshipReference, EmbeddedElement
# from flask_boiler.view_model import ViewModel
from flask_boiler.collection_mixin import CollectionMixin
from flask_boiler.model_registry import ModelRegistry
from flask_boiler.serializable import Serializable
from flask_boiler.factory import ClsFactory
from flask_boiler.utils import snapshot_to_obj


class FirestoreObjectMixin:

    def __init__(self, *args, doc_ref=None, transaction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._doc_ref = doc_ref
        self.transaction = transaction

    def get_firestore_ref(self):
        warnings.warn("Please use .doc_ref instead. ", DeprecationWarning)
        return self.doc_ref

    @property
    def doc_ref(self) -> DocumentReference:
        """ Returns the Document Reference of this object.
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
        """ Retrieves an object from Firestore

        :param doc_ref:
        :param transaction:
        :param kwargs:
        :return:
        """
        if transaction is None:
            snapshot = doc_ref.get()
        else:
            snapshot = doc_ref.get(transaction=transaction)
        obj = snapshot_to_obj(
            snapshot=snapshot,
            super_cls=cls,
            transaction=transaction)
        return obj

    @classmethod
    def from_snapshot(cls, snapshot=None):
        """ Deserializes an object from a Document Snapshot.

        :param snapshot: Firestore Snapshot
        :return:
        """
        obj = snapshot_to_obj(snapshot=snapshot, super_cls=cls)
        return obj

    def save(self, transaction: Transaction = None, doc_ref=None, save_rel=True):
        """ Save an object to Firestore

        :param transaction: Firestore Transaction
        :param doc_ref: override save with this doc_ref
        :param save_rel: If true, objects nested in this
            object will be saved to the Firestore.
        :return:
        """
        if doc_ref is None:
            doc_ref = self.doc_ref

        d = self._export_as_dict(to_save=save_rel)

        if transaction is None:
            doc_ref.set(document_data=d)
        else:
            transaction.set(reference=doc_ref,
                            document_data=d)

    def delete(self, transaction: Transaction = None):
        """ Deletes and object from Firestore.

        :param transaction:
        :return:
        """
        if transaction is None:
            self.doc_ref.delete()
        else:
            transaction.delete(reference=self.doc_ref)


class FirestoreObjectValMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _export_val(self, val, transaction=None, to_save=False):

        def is_nested_relationship(val):
            return isinstance(val, RelationshipReference) and val.nested

        def is_ref_only_relationship(val):
            return isinstance(val, RelationshipReference) and not val.nested

        def nest_relationship(obj):
            if transaction is None:
                obj.save()
            else:
                obj.save(transaction=transaction)
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

    def _export_as_dict(self, **kwargs):
        return super()._export_as_dict(**kwargs,
                                       transaction=self.transaction)

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
                return snapshot_to_obj(snapshot, transaction=transaction)
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

    @classmethod
    def from_dict(cls, d, to_get=True, must_get=False, transaction=None, **kwargs):
        """ Deserializes an object from a dictionary.

        :param d: a dictionary representation of an object generated
            by `to_dict` method.
        :param transaction: Firestore transaction for retrieving
            related documents, and for saving this object.
        :param kwargs:
        :return:
        """

        super_cls, obj_cls = cls, cls

        if "obj_type" in d:
            obj_type = d["obj_type"]
            obj_cls = ModelRegistry.get_cls_from_name(obj_type)

            if obj_cls is None:
                raise ValueError("Cannot read obj_type: {}. "
                                 "Make sure that obj_type is a subclass of {}. "
                                 .format(obj_type, super_cls))

        d = obj_cls.get_schema_obj().load(d)

        def apply(val):
            if isinstance(val, dict):
                return {k: obj_cls._import_val(
                    v,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction)
                    for k, v in val.items()
                }
            elif isinstance(val, list):
                return [obj_cls._import_val(
                    v,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction)
                    for v in val]
            else:
                return obj_cls._import_val(
                    val,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction)

        d = {
            key: apply(val)
            for key, val in d.items() if val != fields.allow_missing
        }

        instance = obj_cls.new(**d, transaction=transaction, **kwargs)  # TODO: fix unexpected arguments
        return instance


class FirestoreObject(FirestoreObjectValMixin,
                      FirestoreObjectMixin,
                      Serializable):
    pass
