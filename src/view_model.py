from typing import Dict, Tuple

from google.cloud.firestore_v1 import DocumentReference
from marshmallow import MarshalResult

from src.domain_model import DomainModel
from src.firestore_object import FirestoreObject
from src.serializable import Serializable


class ViewModel(FirestoreObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.business_properties: Dict[str, Tuple[str, DomainModel]] = dict()

    def bind_to(self, key, foreign_key_str):
        # doc_ref: DocumentReference = DocumentReference(foreign_key_str)
        # obj: DomainModel =
        # self.business_properties[key] =
        raise NotImplementedError

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data
