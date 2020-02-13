import typing

from google.cloud.firestore import DocumentReference
from marshmallow import fields

from flask_boiler.helpers import RelationshipReference, EmbeddedElement
from flask_boiler.serializable import Serializable, Importable, Exportable
from datetime import datetime


class Field(fields.Field):
    """
    Custom class of field for supporting flask_boiler-related
        features such as auto-initialization.
    """

    @property
    def default_value(self):
        """ The default value to assign to instance variable at
                initialization to auto initialize the object.

        :return:
        """
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


class Dict(fields.Raw, Field):

    @property
    def default_value(self):
        return dict()


class Function(fields.Function, Field):
    """
    For use with property.
    """

    @property
    def default_value(self):
        return None


class String(fields.String, Field):

    @property
    def default_value(self):
        return str()


class Nested(fields.Nested, Field):
    """
    Field that describes a dictionary that conforms to a marshmallow schema.
    """

    @property
    def default_value(self):
        return None


class Relationship(fields.Str, Field):
    """
    Field that describes a relationship in reference to another document
        in the Firestore.
    """

    @property
    def default_value(self):
        if self.many:
            return list()
        else:
            return None

    def __init__(self, *args, nested=False, many=False, **kwargs):
        """ Initializes a relationship. A field of the master object
                to describe relationship to another object or document
                being referenced.

        :param args: Positional arguments to pass to marshmallow.fields.Str
        :param nested: If set to True, the document being referenced
                    will be retrieved and saved as the master document
                    or object. If set to False, only the reference
                    (DocumentReference) will be stored in the master
                    document and retrieved into the master object.
        :param many: If set to True, will deserialize and serialize the field
                    as a list. (TODO: add support for more iterables)
        :param kwargs: Keyword arguments to pass to marshmallow.fields.Str
        """
        super().__init__(*args, **kwargs)
        self.nested = nested
        self.many = many

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


class StructuralRef(fields.Str, Field):

    @property
    def default_value(self):
        if self.many:
            return dict()
        else:
            return None

    def __init__(self, *args, nested=False, many=False, dm_cls, **kwargs):
        """ Initializes a relationship. A field of the master object
                to describe relationship to another object or document
                being referenced.

        :param args: Positional arguments to pass to marshmallow.fields.Str
        :param many: If set to True, will deserialize and serialize the field
                    as a dict. (TODO: add support for more iterables)
        :param kwargs: Keyword arguments to pass to marshmallow.fields.Str
        """
        super().__init__(*args, **kwargs)
        self.many = many
        self.dm_cls = dm_cls


class Embedded(fields.Raw, Field):
    """
    Note that when many is set to True, default value of this field
        is an empty list (even if a dict is expected).
    """

    @property
    def default_value(self):
        if self.many:
            return list()
        else:
            return None

    def __init__(self, *args, many=False, **kwargs):
        """

        :param args: Positional arguments to pass to marshmallow.fields.Str
        :param many: If set to True, will deserialize and serialize the field
                    as a list. (TODO: add support for more iterables)
        :param kwargs: Keyword arguments to pass to marshmallow.fields.Str
        """
        super().__init__(*args, **kwargs)
        self.many = many

    def _serialize(self, value, *args, embed_many=None, **kwargs):
        if embed_many is None:
            embed_many = self.many

        if embed_many:
            if isinstance(value, list):
                return [self._serialize(val, embed_many=False)
                        for val in value]
            elif isinstance(value, dict):
                return {
                    key: self._serialize(val, embed_many=False)
                    for key, val in value.items()
                }
            else:
                raise NotImplementedError
        else:
            return EmbeddedElement(
                obj=value
            )

    def _deserialize(self, value, *args, embed_many=None, **kwargs):
        if embed_many is None:
            embed_many = self.many

        if embed_many:
            if isinstance(value, list):
                return [self._deserialize(
                    val, *args, **kwargs, embed_many=False)
                        for val in value]
            elif isinstance(value, dict):
                return {
                    key: self._deserialize(
                        val, *args, **kwargs, embed_many=False)
                    for key, val in value.items()
                }
            else:
                raise NotImplementedError
        else:
            return EmbeddedElement(
                d=value
            )


class Localtime(fields.NaiveDateTime, Field):

    def _serialize(
        self, value, *args, **kwargs
    ):
        if value is None:
            return None
        value = datetime.fromtimestamp(value)
        return super()._serialize(value, *args, **kwargs)

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return None
        value = super()._deserialize(value, *args, **kwargs)
        return value.timestamp()


class Remainder(fields.Dict, Field):
    """
    To match fields that are not declared.
    """

    pass


# class BpStoreField(fields.Raw, Field):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, data_key="_structure", **kwargs)
#         self.many = many


Str = String
