from marshmallow import Schema, MarshalResult

from src.schema import generate_schema
from src.serializable import Serializable
from .context import Context as CTX
from .utils import random_id


class DomainModel(Serializable):

    @property
    def collection_name(self):
        if type(self) == DomainModel:
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

    def _import_doc(self):
        d = self.doc_ref.get().to_dict()
        # TODO: handle errors
        deserialized, _ = self._schema.load(d)
        self._import_properties(deserialized)

    def save(self):
        d = self._export_as_dict()
        self.doc_ref.set(document_data=d)

    @classmethod
    def get(cls, doc_id):
        obj = cls(doc_id=doc_id)
        obj._import_doc()
        return obj

