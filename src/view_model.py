from typing import Dict

from marshmallow import MarshalResult

from src.domain_model import DomainModel
from src.serializable import Serializable


class ViewModel(Serializable):

    def __init__(self):
        super().__init__()
        self.business_properties: Dict[str, DomainModel] = dict()

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data
