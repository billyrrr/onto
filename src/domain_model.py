from marshmallow import Schema, MarshalResult

from src.schema import generate_schema
from .context import Context as CTX
from .utils import random_id


class DomainModel(Schema):

    @property
    def collection_name(self):
        if type(self) == DomainModel:
            raise ValueError("collection_name is read from class name, "
                             "only subclass is supported. ")
        return self.__class__.__name__

    @property
    def collection(self):
        return CTX.db.collection(self.collection_name)

    def __init__(self):
        self._schema = generate_schema(self)

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data

    def save(self):
        d = self._schema.dump(self).data
        doc_id = random_id()
        self.collection.document(doc_id).set(document_data=d)
