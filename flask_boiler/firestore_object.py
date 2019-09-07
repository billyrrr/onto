from google.cloud.firestore import Transaction, CollectionReference, DocumentSnapshot
from google.cloud.firestore import DocumentReference
from marshmallow import Schema, MarshalResult
import warnings

from marshmallow.utils import is_iterable_but_not_string

from flask_boiler.helpers import RelationshipReference
from .schema import generate_schema
from .serializable import Serializable, SerializableClsFactory
from .context import Context as CTX
from .utils import random_id


class FirestoreObjectClsFactory(SerializableClsFactory):
    pass


class FirestoreObject(Serializable):

    def __init__(self, doc_ref=None):
        super().__init__()
        self._doc_ref = doc_ref
        self.transaction = None

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

    def _import_doc(self, d, to_get=False):
        # TODO: handle errors
        deserialized, _ = self.schema_obj.load(d)
        self._import_properties(deserialized, to_get=to_get)

    def get(self, *, doc_ref=None, **kwargs):
        raise NotImplementedError("Must implement in subclass. ")

    def save(self, transaction: Transaction=None):
        d = self._export_as_dict(to_save=True)
        if transaction is None:
            self.doc_ref.set(document_data=d)
        else:
            transaction.set(reference=self.doc_ref,
                            document_data=d)

    def delete(self, transaction: Transaction=None):
        if transaction is None:
            self.doc_ref.delete()
        else:
            transaction.delete(reference=self.doc_ref)

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
                return val
        elif is_ref_only_relationship(val):
            return val.doc_ref
        else:
            return super()._import_val(val)

    def _export_val(self, val, to_save=False):

        def is_nested_relationship(val):
            return isinstance(val, FirestoreObject)

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
                return nest_relationship(val)
            else:
                return val
        elif is_ref_only_relationship(val):
            return val.doc_ref
        else:
            return super()._export_val(val, to_save=to_save)


class ReferencedObject(FirestoreObject):
    """
    ReferencedObject may be placed anywhere in the database.
    """

    @property
    def doc_ref(self):
        return self._doc_ref

    @classmethod
    def get(cls, *, doc_ref=None, transaction: Transaction = None):
        """ Returns an instance from firestore document reference.

        :param doc_ref: firestore document reference
        :param transaction: firestore transaction
        :return:
        """
        obj = cls(doc_ref=doc_ref)
        if transaction is None:
            d = obj.doc_ref.get().to_dict()
        else:
            obj.transaction = transaction
            d = obj.doc_ref.get(transaction=transaction).to_dict()
        obj._import_doc(d, to_get=True)
        return obj


def snapshot_to_obj(snapshot: DocumentSnapshot, super_cls=None):
    d = snapshot.to_dict()
    obj_type = d["obj_type"]
    obj_cls = super_cls.get_subclass_cls(obj_type)

    if obj_cls is None:
        raise ValueError("Cannot read obj_type: {}. "
                         "Make sure that obj_type is a subclass of {}. "
                         .format(obj_type, super_cls))

    if super_cls is not None:
        assert issubclass(obj_cls, super_cls)

    obj = obj_cls.create(doc_id=snapshot.id)
    obj._import_doc(d, to_get=True)
    return obj


def convert_query_ref(func):
    """ Converts a generator of firestore DocumentSnapshot's to a generator
        of objects

    :param super_cls:
    :return:
    """
    def call(cls, *args, **kwargs):
        query_ref = func(cls, *args, **kwargs)
        for res in query_ref.stream():
            assert isinstance(res, DocumentSnapshot)
            yield snapshot_to_obj(snapshot=res, super_cls=cls)
    return call


class PrimaryObject(FirestoreObject):
    """
    Primary Object is placed in a collection in root directory only.
    the document will be stored in and accessed from
            self.collection.document(doc_id)

    Attributes
    ----------
    _collection_name : str
        the name of the collection for the object. Note that different
            types of objects may share one collection.

    """

    # Abstract property: MUST OVERRIDE
    # TODO: add abstract property decorator
    _collection_name = None

    def __init__(self, doc_id=None, doc_ref=None):
        if doc_ref is None:
            doc_ref = self._doc_ref_from_id(doc_id=doc_id)

        super().__init__(doc_ref=doc_ref)

    @classmethod
    def _doc_ref_from_id(cls, doc_id):
        return cls._get_collection().document(doc_id)

    @property
    def collection_name(self):
        """ Returns the root collection name of the class of objects.
                If cls._collection_name is not specified, then the collection
                name will be inferred from the class name.

        :return:
        """
        # if type(self) == FirestoreObject:
        #     raise ValueError("collection_name is read from class name, "
        #                      "only subclass is supported. ")
        return self._get_collection_name()

    @classmethod
    def _get_collection_name(cls):
        if cls._collection_name is None:
            cls._collection_name = cls.__name__
        return cls._collection_name

    @property
    def collection(self):
        """ Returns the firestore collection of the current object

        :return:
        """
        return self._get_collection()

    @classmethod
    def _get_collection(cls):
        return CTX.db.collection(cls._get_collection_name())

    @property
    def doc_id(self):
        return self.doc_ref.id

    @property
    def doc_ref(self):
        if self._doc_ref is None:
            self._doc_ref = self.collection.document(random_id())
        return self._doc_ref

    @classmethod
    def all(cls):
        """ Generator for all objects in the collection

        :return:
        """
        docs_ref: CollectionReference = cls._get_collection()
        docs = docs_ref.stream()
        for doc in docs:
            assert isinstance(doc, DocumentSnapshot)
            obj = cls.create(doc_id=doc.id)
            obj._import_doc(doc.to_dict())
            yield obj

    @classmethod
    @convert_query_ref
    def where(cls, *args, **kwargs):
        """ Note that indexes may need to be added from the link provided
                by firestore in the error messages

        TODO: add error handling and argument checking

        :param args:
        :param kwargs:
        :return:
        """

        if len(args) == 0 and len(kwargs) == 0:
            raise ValueError("Empty where")

        cur_where = cls._get_collection()

        if len(args) != 0:
            if len(args) % 3 != 0:
                raise ValueError
            else:
                arg_stack = list( args )

                while len(arg_stack) != 0:

                    cur_where = cur_where.where(
                        arg_stack.pop(0),
                        arg_stack.pop(0),
                        arg_stack.pop(0)
                    )

        for key, val in kwargs.items():
            cur_where = cur_where.where(key, "==", val)

        return cur_where

    @classmethod
    def create(cls, doc_id=None):
        """
        Creates an instance of object and assign a firestore
            reference with random id to the instance.
        :return:
        """
        if doc_id is None:
            doc_id = random_id()
        doc_ref = cls._get_collection().document(doc_id)
        obj = super().create(doc_ref=doc_ref)
        return obj

    @classmethod
    def get(cls, *, doc_ref_str=None, doc_ref=None, doc_id=None,
            transaction: Transaction=None):
        """ Returns the instance from doc_id.

        :param doc_ref_str: DocumentReference path string
        :param doc_ref: DocumentReference
        :param doc_id: gets the instance from self.collection.document(doc_id)
        :param transaction: firestore transaction
        :return:
        """

        if doc_ref_str is not None:
            doc_ref = CTX.db.document(doc_ref_str)

        if doc_ref is None:
            doc_ref = cls._get_collection().document(doc_id)

        if transaction is None:
            snapshot = doc_ref.get()
        else:
            snapshot = doc_ref.get(transaction=transaction)

        obj = snapshot_to_obj(snapshot=snapshot, super_cls=cls)

        return obj
