from google.cloud.firestore import DocumentReference
from marshmallow import fields

from flask_boiler.helpers import RelationshipReference


class Field(fields.Field):

    @property
    def default_value(self):
        return None


class Boolean(fields.Bool, Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    @property
    def default_value(self):
        return bool()


class Integer(fields.Integer, Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    @property
    def default_value(self):
        return int()


class Raw(fields.Raw, Field):

    @property
    def default_value(self):
        return None


class List(fields.Raw, Field):
    # TODO: change

    @property
    def default_value(self):
        return list()


class Function(fields.Function, Field):

    @property
    def default_value(self):
        _x = None

        def fset(x):
            _x = x

        return property(fget=lambda: _x, fset=fset)


class String(fields.String, Field):

    @property
    def default_value(self):
        return str()


class Nested(fields.Nested, Field):

    @property
    def default_value(self):
        return None


class Relationship(fields.Str, Field):

    def __init__(self, *args, nested=False, many=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested = nested
        self.many = many

    # def _serialize(self, value, *args, **kwargs):
    #     if isinstance(value, list) and self.many:
    #         return [self._serialize(val, *args, **kwargs) for val in value]
    #     else:
    #         if value is None:
    #             raise ValueError
    #         # Note that AssertionError is not always thrown
    #         if self.nested:
    #             return value
    #         else:
    #             assert isinstance(value, DocumentReference)
    #             return RelationshipReference(doc_ref=value,
    #                                          nested=False)
    #
    # def _deserialize(self, value, *args, **kwargs):
    #     if isinstance(value, list) and self.many:
    #         return [self._deserialize(val, *args, **kwargs) for val in value]
    #     else:
    #         if value is None:
    #             raise ValueError
    #         assert isinstance(value, DocumentReference)
    #         return RelationshipReference(
    #             doc_ref=value,
    #             nested=self.nested,
    #         )

    def _serialize(self, value, *args, **kwargs):
        if value is None:
            raise ValueError

        if isinstance(value, list) and self.many:
            return [self._serialize(val, *args, **kwargs) for val in value]

        if isinstance(value, DocumentReference):
            # Note that AssertionError is not always thrown
            return RelationshipReference(doc_ref=value, nested=self.nested)
        else:
            return RelationshipReference(obj=value, nested=self.nested)

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            raise ValueError

        if isinstance(value, list) and self.many:
            return [self._deserialize(val, *args, *kwargs) for val in value]

        assert isinstance(value, DocumentReference)
        return RelationshipReference(
            doc_ref=value,
            nested=self.nested
        )


Str = String
