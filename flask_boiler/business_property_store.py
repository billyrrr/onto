from flask_boiler.schema import Schema
from flask_boiler.serializable import Schemed


class BusinessPropertyStore(Schemed):

    def _get_property_object(self, key):

        if not isinstance(key, str):
            """
            Key must be deep copied 
            """
            raise TypeError

        def getter(_self):
            return _self.store.get_by_key(key)

        return property(fget=getter)

    @classmethod
    def from_schema(cls, schema: Schema):
        class Store(cls):
            _schema_cls = schema
        return Store

    def __init__(self):
        self.fmap = dict()
        self.gmap = dict()
        self.d = dict()

        fd = self._get_fields()  # Calls classmethod

        for key, val in fd.items():
            setattr(self, key, val.default_value)

    def set(self, *, key, property_cls, _id, val):
        if isinstance(self.fmap[key], list):
            self.fmap[key].add( (property_cls, _id) )
            self.gmap[(property_cls, _id)] = key
        else:
            self.fmap[key] = (property_cls, _id)
            self.gmap[(property_cls, _id)] = key
        self.d[(property_cls, _id)] = val

    def get_by_key(self, key):
        res = dict()
        for property_cls, _id in self.fmap[key]:
            res[_id] = self.d[(property_cls, _id)]
        return res
