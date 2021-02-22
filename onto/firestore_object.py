# from google.cloud.firestore import DocumentReference
import abc

# from google.cloud.firestore_v1 import WriteOption, LastUpdateOption

from onto.common import _NA
from onto.database import Snapshot, Reference
from onto.mapper.helpers import RelationshipReference
# from onto.view_model import ViewModel
from onto.models.mixin import resolve_obj_cls
from onto.registry import ModelRegistry
from onto.models.base import Serializable
from onto.utils import snapshot_to_obj
from onto.context import Context as CTX


class FirestoreObjectMixin:

    def __init__(self, *args, doc_ref=None, transaction=_NA, **kwargs):

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        self._doc_ref = doc_ref
        self.transaction = transaction

        super().__init__(*args, **kwargs)

    # def get_firestore_ref(self):
    #     warnings.warn("Please use .doc_ref instead. ", DeprecationWarning)
    #     return self.doc_ref

    @classmethod
    @abc.abstractmethod
    def _datastore(cls):
        pass

    @property
    def doc_ref(self) -> Reference:
        """ Returns the Document Reference of this object.
        """
        return self._doc_ref

    @classmethod
    def get(cls, *, doc_ref=None, transaction=_NA, **kwargs):
        """ Retrieves an object from Firestore

        :param doc_ref:
        :param transaction:
        :param kwargs: Keyword arguments to be forwarded to from_dict
        """

        snapshot = cls._datastore().get(ref=doc_ref, transaction=transaction)
        obj = snapshot_to_obj(
            snapshot=snapshot,
            reference=doc_ref,
            super_cls=cls,
            transaction=transaction)
        return obj

    @classmethod
    def from_snapshot(cls, ref, snapshot=None, **kwargs):
        """ Deserializes an object from a Document Snapshot.

        :param snapshot: Firestore Snapshot
        """
        # if not snapshot.exists:
        #     return None

        obj = cls.from_dict(d=snapshot.to_dict(), doc_ref=ref, **kwargs)
        return obj

    def to_snapshot(self):
        return Snapshot(**self.to_dict())

    def save(self,
             transaction: 'google.cloud.firestore.Transaction'=_NA,
             doc_ref=None,
             _store=_NA,
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

        if _store is _NA:
            if issubclass(self.__class__, FirestoreObjectValMixin):
                _store = self._store
            else:
                _store = None

        d = self._export_as_dict(transaction=transaction, _store=_store)
        _store.save()
        snapshot = Snapshot(d)
        self._datastore().set(snapshot=snapshot, ref=doc_ref, transaction=transaction)

    def delete(self, transaction: 'google.cloud.firestore.Transaction' = _NA) -> None:
        """ Deletes and object from Firestore.

        :param transaction: Firestore Transaction
        """

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        self._datastore().delete(ref=self.doc_ref, transaction=transaction)


def _nest_relationship_import(rr, _store):
    """ (Experimental)

    :param rr:
    :param container:
    :return:
    """
    if rr.obj is not None:
        return rr.obj

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


# def _get_snapshots(transaction, **kwargs):
#     """ needed because transactional wrapper uses specific argument
#         ordering
#
#     :param transaction:
#     :param kwargs:
#     :return:
#     """
#     return CTX.db.get_many(transaction=transaction, **kwargs)


class FirestoreObjectValMixin:
    """
    Subclasses of this class can hold FirestoreObject as an attribute
    """

    @classmethod
    @abc.abstractmethod
    def _datastore(cls):
        """
        NOTE: this is declared in all of:
            - FirestoreObjectMixin
            - FirestoreObjectValMixin
        :return:
        """
        pass

    def __init__(self, *args, _store=_NA, **kwargs):

        if _store is _NA:
            """ NOTE: This branch should only be invoked for objects that are 
                created with new and never retrieved from datastore.
            """
            from onto.store import Gallery
            _store = Gallery()

        self._store = _store
        super().__init__(*args, **kwargs)

    def _export_val(self, val, transaction=None, _store=None):

        def nest_relationship(obj):
            if _store is None:
                # TODO: change
                obj.save(transaction=transaction)
            else:
                _store.save_later(obj, transaction=transaction)

            return str(obj.doc_ref)

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

    def _export_as_dict(self, transaction=None, _store=_NA, **kwargs):

        d = self.schema_obj.dump(self)

        if _store is _NA:
            from onto.store import Gallery
            _store = self._store
            res = self._export_val(d, transaction=transaction, _store=_store,
                                   **kwargs)
            _store.refresh(transaction=transaction)
        else:
            res = self._export_val(d, transaction=transaction, _store=_store,
                                   **kwargs)

        return res

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
    def _import_val(cls, val, transaction=None, partial=False, _store=None):
        # TODO: note partial is not applied to _nest_relationship_import calls
        if isinstance(val, RelationshipReference):
            if val.nested and val.doc_ref is not None:
                return _nest_relationship_import(val, _store=_store)
            elif not val.nested and val.doc_ref is not None:
                return val.doc_ref
            elif val.nested and val.obj is not None:
                return _nest_relationship_import(val, _store=_store)
            else:
                raise ValueError
        else:
            return super()._import_val(val, transaction=transaction, partial=partial, _store=_store)

    @classmethod
    def _import_from_dict(cls, d, transaction=None, _store=_NA, **kwargs):
        if _store is _NA:
            from onto.store import Gallery
            _store = Gallery()
            res = cls._import_val(d, transaction=transaction, _store=_store, **kwargs)
            _store.refresh(transaction=transaction)
        else:
            res = cls._import_val(d, transaction=transaction, _store=_store,
                                  **kwargs)
        res['_store'] = _store
        return res

    @classmethod
    def from_dict(
            cls,
            d,
            _store=_NA,
            transaction=None,
            partial=False,
            **kwargs):
        """ Deserializes an object from a dictionary.

        :param d: a dictionary representation of an object generated
            by `to_dict` method.
        :param transaction: Firestore transaction for retrieving
            related documents, and for saving this object.
        :param kwargs: Keyword arguments to be forwarded to new
        """

        obj_cls = resolve_obj_cls(cls=cls, d=d)

        schema_obj = obj_cls.get_schema_obj()
        d = schema_obj.load(d, partial=partial)

        d = cls._import_from_dict(d, _store=_store, partial=partial, transaction=transaction)

        instance = obj_cls.new(**d, **kwargs)
        # TODO: fix unexpected arguments
        return instance


class FirestoreObject(
    FirestoreObjectValMixin,
                      FirestoreObjectMixin,
                      Serializable):

    @classmethod
    def _datastore(cls):
        _db = CTX.db
        return _db
