import typing

import iso8601
import pytz
from google.cloud.firestore import DocumentReference
from marshmallow import fields

from flask_boiler.helpers import RelationshipReference, EmbeddedElement
from flask_boiler.serializable import Serializable, Importable, Exportable
from datetime import datetime
from math import inf

from marshmallow import utils as mutils


# Firestore Integer supports up to 64-bit signed
# Note that this may result in defect where business data reaches
#   this maximum.
_POS_INF_APPROX = 2**63 - 1
_NEGATIVE_INF_APPROX = -2**63


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
        if self.default == mutils.missing:
            return None
        else:
            value = self.default() if callable(self.default) else self.default
            return value


class Boolean(fields.Bool, Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    @property
    def default_value(self):
        return bool()


class NumberTimestamp(fields.Raw, Field):
    pass


class Integer(fields.Integer, Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    @property
    def default_value(self):
        return int()

    def _serialize(self, value, *args, **kwargs):
        if value == inf:
            return _POS_INF_APPROX
        elif value == -inf:
            return _NEGATIVE_INF_APPROX
        else:
            return value

    def _deserialize(self, value, *args, **kwargs):
        if value >= _POS_INF_APPROX:
            return inf
        elif value <= _NEGATIVE_INF_APPROX:
            return -inf
        else:
            return value


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
            return None
            # raise ValueError

        if isinstance(value, list) and self.many:
            return [self._serialize(val, *args, **kwargs) for val in value]
        elif isinstance(value, dict) and self.many:
            val_d = dict()
            for k, v in value.items():
                val_d[k] = self._serialize(v, *args, **kwargs)
            return val_d

        if isinstance(value, DocumentReference):
            # Note that AssertionError is not always thrown
            return RelationshipReference(doc_ref=value, nested=self.nested)
        else:
            return RelationshipReference(obj=value, nested=self.nested)

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return None
            # raise ValueError

        if isinstance(value, list) and self.many:
            return [self._deserialize(val, *args, *kwargs) for val in value]
        elif isinstance(value, dict) and self.many:
            val_d = dict()
            for k, v in value.items():
                val_d[k] = self._deserialize(v, *args, **kwargs)
            return val_d

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


def local_time_from_timestamp(timestamp) -> str:
    """

    :param timestamp: for example: 1545062400
    :return: for example: "2018-12-17T08:00:00"
    """
    tz = pytz.timezone('US/Pacific') #('America/Los_Angeles')

    d: datetime = datetime.fromtimestamp(timestamp, tz=tz)
    d = d.replace(tzinfo=None) # Convert to local time
    return d.isoformat()


def str_to_local_time(s) -> datetime:
    tz = pytz.timezone('America/Los_Angeles')
    return tz.localize(iso8601.parse_date(s, default_timezone=None))


def timestamp_from_local_time(s) -> int:
    return int(str_to_local_time(s).timestamp())


class Localtime(fields.NaiveDateTime, Field):

    def _serialize(
        self, value, *args, **kwargs
    ):
        if value is None:
            return None
        else:
            return local_time_from_timestamp(value)

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return mutils.missing
        else:
            return timestamp_from_local_time(value)


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
