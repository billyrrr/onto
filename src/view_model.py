from typing import Dict, Tuple

from google.cloud.firestore import DocumentReference
from marshmallow import MarshalResult

from .domain_model import DomainModel
from .firestore_object import ReferencedObject
from .serializable import Serializable


class ViewModel(ReferencedObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.business_properties: Dict[str, Tuple[str, DomainModel]] = dict()

    def bind_to(self, key, foreign_key_str):
        # doc_ref: DocumentReference = DocumentReference(foreign_key_str)
        # obj: DomainModel =
        # self.business_properties[key] =
        raise NotImplementedError

    def to_dict(self):
        mres: MarshalResult = self.schema_obj.dump(self)
        return mres.data

