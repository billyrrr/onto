from typing import List, Dict

from marshmallow import MarshalResult

from src.domain_model import DomainModel
from src.schema import generate_schema


class ViewModel:

    def __init__(self):
        self._schema = generate_schema(self)
        self.business_properties: Dict[str, DomainModel] = dict()

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data
