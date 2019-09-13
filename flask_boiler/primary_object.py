from google.cloud.firestore_v1 import DocumentSnapshot, CollectionReference, \
    Transaction

from flask_boiler.context import Context as CTX
from flask_boiler.firestore_object import snapshot_to_obj, FirestoreObject
from flask_boiler.utils import random_id


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
            obj._import_properties(doc.to_dict())
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
    def create(cls, doc_id=None, doc_ref=None):
        """
        Creates an instance of object and assign a firestore
            reference with random id to the instance.
        :return:
        """
        if doc_ref is None:

            if doc_id is None:
                doc_id = random_id()
            doc_ref = cls._get_collection().document(doc_id)
            obj = super().create(doc_ref=doc_ref)
            return obj

        else:

            assert doc_id is None
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

        return super().get(doc_ref=doc_ref, transaction=transaction)