from google.cloud.firestore import Transaction
from marshmallow import Schema, MarshalResult

from .schema import generate_schema
from .serializable import Serializable
from .context import Context as CTX
from .utils import random_id


class FirestoreObject(Serializable):

    @property
    def doc_ref(self):
        """
        Must be implemented in subclass
        """
        raise NotImplementedError

    def _import_doc(self, d):
        # TODO: handle errors
        deserialized, _ = self._schema.load(d)
        self._import_properties(deserialized)

    def save(self, transaction: Transaction=None):
        d = self._export_as_dict()
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


class ReferencedObject(FirestoreObject):
    """
    ReferencedObject may be placed anywhere in the database.
    """

    @property
    def doc_ref(self):
        return self._doc_ref

    def __init__(self, doc_ref=None):
        super().__init__()
        self._doc_ref = doc_ref

    @classmethod
    def create(cls, doc_ref=None):
        if doc_ref is None:
            raise ValueError
        obj = cls(doc_ref=doc_ref)
        return obj

    @classmethod
    def get(cls, doc_ref, transaction: Transaction = None):
        obj = cls(doc_ref=doc_ref)
        if transaction is None:
            d = obj.doc_ref.get().to_dict()
        else:
            d = obj.doc_ref.get(transaction=transaction).to_dict()
        obj._import_doc(d)
        return obj


class PrimaryObject(FirestoreObject):
    """
    Primary Object is placed in a collection in root directory only.
    """

    @property
    def collection_name(self):
        if type(self) == FirestoreObject:
            raise ValueError("collection_name is read from class name, "
                             "only subclass is supported. ")
        return self.__class__.__name__

    @property
    def collection(self):
        return CTX.db.collection(self.collection_name)

    @property
    def doc_id(self):
        if self._doc_id is None:
            self._doc_id = random_id()
        return self._doc_id

    @property
    def doc_ref(self):
        return self.collection.document(self.doc_id)

    def __init__(self, doc_id=None):
        super().__init__()
        self._doc_id = doc_id

    @classmethod
    def create(cls, doc_id=None):
        """
        Create an instance of object and assign a Firestore
            reference with random id to the instance.
        :return:
        """
        if doc_id is None:
            doc_id = random_id()
        obj = cls(doc_id=doc_id)
        return obj

    @classmethod
    def get(cls, doc_id, transaction: Transaction=None):
        obj = cls(doc_id=doc_id)
        if transaction is None:
            d = obj.doc_ref.get().to_dict()
        else:
            d = obj.doc_ref.get(transaction=transaction).to_dict()
        obj._import_doc(d)
        return obj
