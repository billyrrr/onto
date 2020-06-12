import warnings

from google.cloud.firestore import DocumentReference
from google.cloud.firestore import Transaction
from google.cloud.firestore_v1 import WriteOption, LastUpdateOption

from flask_boiler import fields
from flask_boiler.common import _NA
from flask_boiler.helpers import RelationshipReference
# from flask_boiler.view_model import ViewModel
from flask_boiler.registry import ModelRegistry
from flask_boiler.models.base import Serializable
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.context import Context as CTX
from flask_boiler.factory import ClsFactory


class FirestoreObjectMixin:

    def __init__(self, *args, doc_ref=None, transaction=_NA, **kwargs):

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        self._doc_ref = doc_ref
        self.transaction = transaction
        super().__init__(*args, **kwargs)

    def get_firestore_ref(self):
        warnings.warn("Please use .doc_ref instead. ", DeprecationWarning)
        return self.doc_ref

    @property
    def doc_ref(self) -> DocumentReference:
        """ Returns the Document Reference of this object.
        """
        raise NotImplementedError

    @property
    def doc_ref_str(self) -> str:
        """ Serializes to doc_ref field.
        """
        return self.doc_ref.path

    @classmethod
    def get(cls, *, doc_ref=None, transaction=_NA, **kwargs):
        """ Retrieves an object from Firestore

        :param doc_ref:
        :param transaction:
        :param kwargs: Keyword arguments to be forwarded to from_dict
        """

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

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
        """
        if not snapshot.exists:
            return None

        obj = cls.from_dict(d=snapshot.to_dict(), doc_ref=snapshot.reference)
        return obj

    def save(self,
             transaction: Transaction=_NA,
             doc_ref=None,
             save_rel=True,
             ):
        """ Save an object to Firestore

        :param transaction: Firestore Transaction
        :param doc_ref: override save with this doc_ref
        :param save_rel: If true, objects nested in this
            object will be saved to the Firestore.
        """

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        if doc_ref is None:
            doc_ref = self.doc_ref

        d = self._export_as_dict(to_save=save_rel, transaction=transaction)

        if transaction is None:
            doc_ref.set(document_data=d)
        else:
            transaction.set(reference=doc_ref,
                            document_data=d)



    def delete(self, transaction: Transaction = _NA) -> None:
        """ Deletes and object from Firestore.

        :param transaction: Firestore Transaction
        """

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        if transaction is None:
            self.doc_ref.delete()
        else:
            transaction.delete(reference=self.doc_ref)


def _nest_relationship_import(rr, store):
    """ (Experimental)

    :param rr:
    :param container:
    :return:
    """

    store.insert(doc_ref=rr.doc_ref, obj_type=rr.obj_type)
    from peak.util.proxies import CallbackProxy
    import functools
    _callback = functools.partial(store.retrieve, doc_ref=rr.doc_ref, obj_type=rr.obj_type)
    return CallbackProxy(_callback)


class RelationshipStore:

    def __init__(self):
        self.queue = list()
        self.container = SnapshotContainer()

    def insert(self, *, doc_ref, obj_type):
        """
        TODO: implement obj_type kwarg or toss it
        :param doc_ref:
        :param obj_type:
        :return:
        """
        self.queue.append(doc_ref)

    def refresh(self, transaction):
        refs = list()
        for doc_ref in self.queue:
            refs.append(doc_ref)

        def get_snapshots(transaction, **kwargs):
            """ needed because transactional wrapper uses specific argument
                ordering

            :param transaction:
            :param kwargs:
            :return:
            """
            return CTX.db.get_all(transaction=transaction, **kwargs)

        res = get_snapshots(references=refs, transaction=transaction)
        for doc in res:
            self.container.set(key=doc.reference._document_path, val=doc)

    def retrieve(self, *, doc_ref, obj_type):
        snapshot = self.container.get(key=doc_ref._document_path)
        return obj_type.from_snapshot(snapshot=snapshot)


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

    # def _export_val_view(self, val):
    #     def is_nested_relationship(val):
    #         return isinstance(val, RelationshipReference) and val.nested
    #
    #     def is_ref_only_relationship(val):
    #         return isinstance(val, RelationshipReference) and not val.nested
    #
    #     if is_nested_relationship(val):
    #         return super()._export_val_view(val.obj)
    #     elif is_ref_only_relationship(val):
    #         return super()._export_val_view(val.doc_ref.path)
    #     else:
    #         return super()._export_val_view(val)

    def _export_as_dict(self, transaction=None, **kwargs):
        if transaction is None:
            transaction = self.transaction
        return super()._export_as_dict(**kwargs,
                                       transaction=transaction)

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
    def _import_val(cls, val, to_get=False, must_get=False, transaction=None, store=None):

        def is_nested_relationship(val):
            return isinstance(val, RelationshipReference) and val.nested

        def is_ref_only_relationship(val):
            return isinstance(val, RelationshipReference) and not val.nested

        def nest_relationship(val: RelationshipReference):
            return _nest_relationship_import(val, store=store)
            # if transaction is None:
            #     snapshot = val.doc_ref.get()
            #     return snapshot_to_obj(snapshot, transaction=transaction)
            # else:
            #     snapshot = val.doc_ref.get(transaction=transaction)
            #     return snapshot_to_obj(snapshot, transaction=transaction)

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
    def from_dict(
            cls,
            d,
            to_get=True,
            must_get=False,
            transaction=None,
            **kwargs):
        """ Deserializes an object from a dictionary.

        :param d: a dictionary representation of an object generated
            by `to_dict` method.
        :param transaction: Firestore transaction for retrieving
            related documents, and for saving this object.
        :param kwargs: Keyword arguments to be forwarded to new
        """

        super_cls, obj_cls = cls, cls

        from flask_boiler.common import read_obj_type
        obj_type_str = read_obj_type(d, obj_cls)

        if obj_type_str is not None:
            """ If obj_type string is specified, use it instead of cls supplied 
                to from_dict. 

            TODO: find a way to raise error when obj_type_str reading 
                fails with None and obj_type evaluates to cls supplied 
                to from_dict unintentionally. 

            """
            obj_cls = ModelRegistry.get_cls_from_name(obj_type_str)
            if obj_cls is None:
                """ If obj_type string is specified but invalid, 
                    throw a ValueError. 
                """
                raise ValueError("Cannot read obj_type string: {}. "
                                 "Make sure that obj_type is a subclass of {}."
                                 .format(obj_type_str, super_cls))

        d = obj_cls.get_schema_obj().load(d)

        _store = RelationshipStore()

        def apply(val):
            if isinstance(val, dict):
                return {k: obj_cls._import_val(
                    v,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction, store=_store)
                    for k, v in val.items()
                }
            elif isinstance(val, list):
                return [obj_cls._import_val(
                    v,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction, store=_store)
                    for v in val]
            else:
                return obj_cls._import_val(
                    val,
                    to_get=to_get,
                    must_get=must_get,
                    transaction=transaction, store=_store)

        d = {
            key: apply(val)
            for key, val in d.items() if val != fields.allow_missing
        }

        _store.refresh(transaction=transaction)

        instance = obj_cls.new(**d, transaction=transaction, **kwargs)  # TODO: fix unexpected arguments
        return instance


class FirestoreObject(FirestoreObjectValMixin,
                      FirestoreObjectMixin,
                      Serializable):
    pass
