from marshmallow import MarshalResult

from src.schema import generate_schema


class ViewModel:

    def __init__(self):
        self._schema = generate_schema(self)

    def to_dict(self):
        mres: MarshalResult = self._schema.dump(self)
        return mres.data
