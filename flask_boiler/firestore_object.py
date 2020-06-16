import warnings

from google.cloud.firestore import DocumentReference
from google.cloud.firestore import Transaction
from google.cloud.firestore_v1 import WriteOption, LastUpdateOption

from flask_boiler import fields
from flask_boiler.common import _NA
from flask_boiler.helpers import RelationshipReference
# from flask_boiler.view_model import ViewModel
from flask_boiler.models.mixin import resolve_obj_cls
from flask_boiler.registry import ModelRegistry
from flask_boiler.models.base import Serializable
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.context import Context as CTX
from flask_boiler.factory import ClsFactory


class FirestoreObjectMixin:

    def __init__(self, *args, doc_ref=None, transaction=_NA, _store=None, **kwargs):

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        self._doc_ref = doc_ref
        self.transaction = transaction
        if _store is None:
            _store = RelationshipStore()
        self._store = _store
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
             _store=None,
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

        d = self._export_as_dict(transaction=transaction, _store=_store)

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


def _nest_relationship_import(rr, _store):
    """ (Experimental)

    :param rr:
    :param container:
    :return:
    """
    doc_ref, obj_type = rr.doc_ref, rr.obj_type
    if isinstance(obj_type, str):
        obj_type = ModelRegistry.get_cls_from_name(obj_type)

    _store.insert(doc_ref=doc_ref, obj_type=obj_type)
    from peak.util.proxies import CallbackProxy
    import functools
    _callback = functools.partial(_store.retrieve, doc_ref=doc_ref, obj_type=obj_type)
    return CallbackProxy(_callback)


# def _nest_relationship_export(rr, store):
#     """ (Experimental)
#
#     :param rr:
#     :param container:
#     :return:
#     """
#     obj, obj_type = rr.obj, rr.obj_type
#
#     store.insert(doc_ref=doc_ref, obj_type=obj_type)
#     from peak.util.proxies import CallbackProxy
#     import functools
#     _callback = functools.partial(store.retrieve, doc_ref=doc_ref, obj_type=obj_type)
#     return CallbackProxy(_callback)


def _get_snapshots(transaction, **kwargs):
    """ needed because transactional wrapper uses specific argument
        ordering

    :param transaction:
    :param kwargs:
    :return:
    """
    return CTX.db.get_all(transaction=transaction, **kwargs)


class RelationshipStore:

    def __init__(self):
        self.tasks = dict()  # TODO: Watch out for when (doc_ref, obj_type_super) and (doc_ref, obj_type_sub) are both in the set; the objects will be equivalent, but initialized twice under the current plan
        self.visited = set()
        self.container = SnapshotContainer()
        self.object_container = dict()
        self.saved = set()

    def insert(self, *, doc_ref, obj_type) -> None:
        """
        TODO: implement obj_type kwarg or toss it
        :param doc_ref:
        :param obj_type:
        :return:
        """
        if doc_ref in self.tasks or doc_ref in self.visited:
            return
        self.tasks[doc_ref] = obj_type
        self.visited.add(doc_ref)

    def refresh(self, transaction, get_snapshots=_get_snapshots):

        while len(self.tasks) != 0:

            refs = list()
            for doc_ref in self.tasks:
                refs.append(doc_ref)

            res = get_snapshots(references=refs, transaction=transaction)
            for doc in res:
                self.container.set(key=doc.reference._document_path, val=doc)
                del self.tasks[doc.reference]

            for doc in res:
                obj_type = self.tasks[doc.reference]
                d = doc.to_dict()
                obj_cls = resolve_obj_cls(cls=obj_type, d=d)

                schema_obj = obj_cls.get_schema_obj()
                d = schema_obj.load(d)
                d = obj_cls._import_from_dict(d, transaction=transaction, _store=self)

                instance = obj_cls.new(**d, transaction=transaction)
                self.object_container[doc.reference] = instance

    def retrieve(self, *, doc_ref, obj_type):
        snapshot = self.container.get(key=doc_ref._document_path)
        return obj_type.from_snapshot(snapshot=snapshot)


class FirestoreObjectValMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _export_val(self, val, transaction=None, _store=None):

        def nest_relationship(obj):
            def _save():
                if transaction is None:
                    obj.save(_store=_store)
                else:
                    obj.save(transaction=transaction, _store=_store)

            if _store is not None and obj.doc_ref not in _store.saved:
                _store.saved.add(obj.doc_ref)
                _save()
            elif _store is None:
                _save()
            return obj.doc_ref

        if isinstance(val, RelationshipReference):
            if val.nested and val.obj is not None:
                return nest_relationship(val.obj)
            elif val.nested and val.doc_ref is not None:
                return val.doc_ref
            elif not val.nested and val.doc_ref is not None:
                return val.doc_ref
            elif not val.nested and val.obj is not None:
                """ We should stay away from serializing a 
                    referenced object in domain model since references on 
                    domain model can be circularly referenced. Such case 
                    results in a loop that may create dangerous amount of 
                    external or internal API usage. 
                """
                raise ValueError
            else:
                return None
        else:
            return super()._export_val(val, transaction=transaction, _store=_store)


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

    def _export_as_dict(self, transaction=None, _store=None, **kwargs):
        if transaction is None:
            transaction = self.transaction
        if _store is None:
            _store = self._store

        return super()._export_as_dict(**kwargs,
                                       transaction=transaction, _store=_store)

    # def _export_val_view(self, val):
    #
    #     def get_vm(doc_ref):
    #         obj = FirestoreObject.get(doc_ref=doc_ref,
    #                                   transaction=self.transaction)
    #         return obj._export_as_view_dict()
    #
    #     if isinstance(val, RelationshipReference):
    #         if val.obj is not None:
    #             return val.obj._export_as_view_dict()
    #         elif val.doc_ref is not None:
    #             return get_vm(val.doc_ref)
    #         else:
    #             return val.doc_ref
    #     else:
    #         return super()._export_val_view(val)

    @classmethod
    def _import_val(cls, val, transaction=None, _store=None):

        if isinstance(val, RelationshipReference):
            if val.nested and val.doc_ref is not None:
                return _nest_relationship_import(val, _store=_store)
            elif not val.nested and val.doc_ref is not None:
                return val.doc_ref
            else:
                return None
        else:
            return super()._import_val(val, transaction=transaction, _store=_store)

    @classmethod
    def _import_from_dict(cls, d, transaction=None, _store=_NA, **kwargs):
        if _store is _NA:
            _store = RelationshipStore()
            res = cls._import_val(d, transaction=transaction, _store=_store, **kwargs)
            _store.refresh(transaction=transaction)
        else:
            res = cls._import_val(d, transaction=transaction, _store=_store,
                                  **kwargs)
        return res

    @classmethod
    def from_dict(
            cls,
            d,
            transaction=None,
            **kwargs):
        """ Deserializes an object from a dictionary.

        :param d: a dictionary representation of an object generated
            by `to_dict` method.
        :param transaction: Firestore transaction for retrieving
            related documents, and for saving this object.
        :param kwargs: Keyword arguments to be forwarded to new
        """
        return super().from_dict(d, transaction=transaction, **kwargs)


class FirestoreObject(FirestoreObjectValMixin,
                      FirestoreObjectMixin,
                      Serializable):
    pass
