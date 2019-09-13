from google.cloud.firestore_v1 import Transaction

from flask_boiler.context import Context as CTX
from flask_boiler.firestore_object import FirestoreObject
from flask_boiler.query_mixin import QueryMixin
from flask_boiler.utils import random_id


class PrimaryObject(FirestoreObject, QueryMixin):
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
