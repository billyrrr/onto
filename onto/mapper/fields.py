import typing
from collections import namedtuple

import iso8601
import pytz
from marshmallow import fields

from onto.common import _NA
from onto.mapper.helpers import RelationshipReference, EmbeddedElement

from datetime import datetime

from marshmallow import utils as mutils

from onto.registry import ModelRegistry

# Firestore Integer supports up to 64-bit signed
# Note that this may result in defect where business data reaches
#   this maximum.
# from onto.models.meta import ModelRegistry

_POS_INF_APPROX = 2 ** 63 - 1
_NEGATIVE_INF_APPROX = -2 ** 63

allow_missing = fields.missing_

OBJ_TYPE_ATTR_NAME = "obj_type"


class Field(fields.Field):
    """
    Custom class of field for supporting onto-related
        features such as auto-initialization.
    """

    def __init__(self,
                 *args, default=fields.missing_,
                 **kwargs):
        super().__init__(*args, default=default, **kwargs)

    @property
    def default_value(self):
        return self.deserialize(fields.missing_)
        # return self.initialize_value() \
        #     if callable(self.initialize_value) \
        #     else self.initialize_value


class Boolean(fields.Bool, Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    def __init__(self, missing=bool, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)

    def __get__(self, instance, owner) -> bool:
        return super().__get__(instance, owner)


class NumberTimestamp(fields.Raw, Field):
    pass


class Integer(fields.Integer, Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    def __init__(self, missing=int, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, int]:
        """
        Type hinting
        """
        pass


class Float(fields.Float, Field):
    """Field that serializes to an float and deserializes
            to an float.
    """

    def __init__(self, missing=float, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, float]:
        """
        Type hinting
        """
        pass


class Raw(fields.Raw, Field):
    pass


class List(fields.List, Field):
    # TODO: change

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, typing.List]:
        """
        Type hinting
        # TODO: prevent this section of code from being accidentally called
            even if typing.overload decorator got accidentally erased
        """
        pass

    def __init__(self, *args, missing=list, **kwargs):
        super().__init__(*args, missing=missing, **kwargs)


class Mapping(fields.Mapping, Field):
    def __init__(self, *args, missing=dict, **kwargs):
        super().__init__(*args, missing=missing, **kwargs)


class Dict(fields.Dict, Field):

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, typing.Dict]:
        """
        Type hinting
        """
        pass

    def __init__(self, *args, missing=dict, **kwargs):
        super().__init__(*args, missing=missing, **kwargs)


class Function(fields.Function, Field):
    """
    For use with property.
    """
    def __init__(self, missing=fields.missing_, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)


class DocIdField(fields.Function, Field):

    def __init__(self, *args, **kwargs):
        def serialize(obj):
            """ serialize: A callable from which to retrieve the value.
            The function must take a single argument ``obj`` which is the object
            to be serialized. It can also optionally take a ``context`` argument,
            which is a dictionary of context variables passed to the serializer.
            If no callable is provided then the ```load_only``` flag will be set

            to True.
            :param obj:
            :return:
            """
            # TODO: delete
            try:
                res = getattr(obj, self.attribute)
            except AttributeError as e:
                return fields.missing_
            else:
                return res

        def deserialize(value):
            """ deserialize: A callable from which to retrieve the value.
            The function must take a single argument ``value`` which is the value
            to be deserialized. It can also optionally take a ``context`` argument,
            which is a dictionary of context variables passed to the deserializer.
            If no callable is provided then ```value``` will be passed through
            unchanged.

            :param value:
            :return:
            """
            data_key = self.data_key
            if data_key not in value:
                return fields.missing_
            else:
                return value[data_key]

        super().__init__(
            *args,
            serialize=serialize,
            deserialize=deserialize,
            **kwargs
        )


from onto.database import Reference


class DocRefField(fields.String, Field):

    def _deserialize(self, value, *args, **kwargs) -> Reference:
        return Reference.from_str(s=value)

    def _serialize(self, value, *args, **kwargs) -> str:
        return str(value)


argument = namedtuple('argument', ['key', 'comparator', 'val'])


class ObjClsMixin:

    def __init__(self, *args, obj_type=_NA, **kwargs):
        if obj_type is _NA:
            from onto.firestore_object import FirestoreObject
            obj_type = FirestoreObject
        self._obj_cls = obj_type
        super().__init__(*args, **kwargs)

    @property
    def obj_cls(self):
        _obj_cls = self._obj_cls
        if isinstance(self._obj_cls, str):
            _obj_cls = ModelRegistry.get_cls_from_name(obj_type_str=_obj_cls)
        return _obj_cls


class ObjectTypeField(fields.Function, Field):

    @staticmethod
    def f_serialize(obj, context):
        """ serialize: A callable from which to retrieve the value.
        The function must take a single argument ``obj`` which is the object
        to be serialized. It can also optionally take a ``context`` argument,
        which is a dictionary of context variables passed to the serializer.
        If no callable is provided then the ```load_only``` flag will be set
        to True.

        :param obj:
        :return:
        """
        # TODO: delete

        try:
            from onto.utils import obj_type_serialize
            res = obj_type_serialize(obj)
        except AttributeError:
            return fields.missing_
        else:
            return res

    def read_obj_type_str(self, raw_dict) -> typing.Optional[str]:
        """ Read obj_type string from inputs that are to be
        deserialized/imported/loaded soon

        :return:
        """
        if self.data_key in raw_dict:
            return raw_dict[self.data_key]
        else:
            return None

    def get_obj_type_data_key(self):
        # NOTE: this is different from not self.dump_only
        # NOTE: load_only and dump_only can be true at the same time
        if self.load_only:
            return None
        else:
            return self.data_key

    def get_obj_type_condition(self, obj_cls) -> typing.Optional[typing.Tuple]:
        data_key = self.get_obj_type_data_key()
        if data_key is None:
            return None
        else:
            return argument(
                key=data_key,
                comparator=obj_cls._datastore().Comparators._in,
                val=obj_cls._get_subclasses_str())

    def __init__(self, *args, serialize=_NA, data_key="obj_type",
                 deserialize=_NA,
                 **kwargs):
        if serialize is _NA:
            serialize = self.f_serialize
        if deserialize is _NA:
            deserialize = None

        super().__init__(
            *args,
            serialize=serialize,
            data_key=data_key,
            deserialize=deserialize,
            **kwargs
        )


class String(fields.String, Field):

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, str]:
        """
        Type hinting
        """
        pass

    def __init__(self, missing=str, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)


class Nested(fields.Nested, Field):
    """
    Field that describes a dictionary that conforms to a marshmallow schema.
    """
    pass


class _MissingNotSpecified:
    pass


class Relationship(ObjClsMixin, fields.Str, Field):
    """
    Field that describes a relationship in reference to another document
        in the Firestore.
    """

    def __init__(self, *args, missing=_MissingNotSpecified, nested=False,
                 many=False, **kwargs):
        """ Initializes a relationship. A field of the master object
                to describe relationship to another object or document
                being referenced. Set missing=dict if many=True and
                data is stored in a dict.

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
        if missing == _MissingNotSpecified:
            missing = list if many else None
        super().__init__(*args, missing=missing, **kwargs)
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

        if not self.nested:
            # Note that AssertionError is not always thrown
            return RelationshipReference(doc_ref=str(value), nested=self.nested)
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

        # assert isinstance(value, DocumentReference)
        from onto.database.firestore import FirestoreReference
        if isinstance(value, str):
            doc_ref = FirestoreReference.from_str(value)
        else:
            doc_ref = FirestoreReference.from_document_reference(value)
        # TODO: change
        return RelationshipReference(
            doc_ref=doc_ref,
            nested=self.nested,
            obj_type=self.obj_cls
        )


class StructuralRef(ObjClsMixin, fields.Str, Field):

    def __init__(self, *args, missing=_MissingNotSpecified,
                 many=False, **kwargs):
        """ Initializes a relationship. A field of the master object
                to describe relationship to another object or document
                being referenced.

        :param args: Positional arguments to pass to marshmallow.fields.Str
        :param many: If set to True, will deserialize and serialize the field
                    as a dict. (TODO: add support for more iterables)
        :param kwargs: Keyword arguments to pass to marshmallow.fields.Str
        """
        if missing == _MissingNotSpecified:
            missing = dict if many else None
        super().__init__(*args, missing=missing, **kwargs)
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

        # if isinstance(value, DocumentReference):
        #     # Note that AssertionError is not always thrown
        #     return RelationshipReference(doc_ref=value, nested=True)
        # else:
        return RelationshipReference(obj=value, nested=True)

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return None
            # raise ValueError
        from onto.store.struct import struct_ref

        if isinstance(value, list) and self.many:

            return [self._deserialize(val, *args, *kwargs) for val in value]

        elif isinstance(value, dict) and self.many:

            val_d = dict()
            for k, v in value.items():
                val_d[k] = self._deserialize(v, *args, **kwargs)
            return val_d

        elif isinstance(value, struct_ref):

            if value.snapshot is not None and value.ref is not None:
                dm_cls, snapshot, ref = value.dm_cls, value.snapshot, value.ref
                obj = dm_cls.from_snapshot(ref=ref, snapshot=snapshot)
                return RelationshipReference(
                    obj=obj,
                    nested=True,
                    obj_type=dm_cls
                )
            elif value.obj is not None:
                obj = value.obj
                return RelationshipReference(
                    obj=obj,
                    nested=True,
                    obj_type=obj.__class__
                )
            elif value.doc_ref is not None:
                dm_cls, doc_ref = value.dm_cls, value.ref
                return RelationshipReference(
                    doc_ref=doc_ref,
                    nested=True,
                    obj_type=dm_cls
                )
            elif value.doc_id is not None:
                dm_cls, doc_id = value.dm_cls, value.id
                doc_ref = self.obj_cls.ref_from_id(doc_id=doc_id)
                return RelationshipReference(
                    doc_ref=doc_ref,
                    nested=True,
                    obj_type=dm_cls
                )
            else:
                raise ValueError

        else:

            dm_cls, doc_id = value
            doc_ref = self.obj_cls.ref_from_id(doc_id=doc_id)
            return RelationshipReference(
                doc_ref=doc_ref,
                nested=True,
                obj_type=dm_cls
            )


class Embedded(ObjClsMixin, fields.Raw, Field):
    """
    Note that when many is set to True, default value of this field
        is an empty list (even if a dict is expected).
    """

    def __init__(self, *args, missing=_MissingNotSpecified, many=False,
                 **kwargs):
        """

        :param args: Positional arguments to pass to marshmallow.fields.Str
        :param many: If set to True, will deserialize and serialize the field
                    as a list. (TODO: add support for more iterables)
        :param obj_cls: cls of the element
        :param kwargs: Keyword arguments to pass to marshmallow.fields.Str
        """

        if missing == _MissingNotSpecified:
            missing = list if many else None
        self.many = many

        super().__init__(*args, missing=missing, **kwargs)

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
                d=value,
                obj_cls=self.obj_cls
            )


def local_time_from_timestamp(timestamp) -> datetime:
    """
    Accurate to seconds
    :param timestamp: for example: 1545062400
    :return: for example: "2018-12-17T08:00:00"
    """
    tz = pytz.timezone('US/Pacific')  # ('America/Los_Angeles')   // TODO: make consistent with str_to_local_time

    d: datetime = datetime.fromtimestamp(timestamp, tz=tz)
    d = d.replace(tzinfo=None)  # Convert to local time
    return d.isoformat()


def str_to_local_time(s) -> datetime:
    tz = pytz.timezone('America/Los_Angeles')
    return tz.localize(iso8601.parse_date(s, default_timezone=None))


def timestamp_from_local_time(s) -> int:
    return int(str_to_local_time(s).timestamp())


class Localtime(fields.NaiveDateTime, Field):

    @typing.overload
    def __get__(self, instance, owner) -> typing.Union[Field, int]:
        """
        Type hinting
        """
        pass

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

    def __init__(self, missing=fields.missing_, *args, **kwargs):
        super().__init__(missing=missing, *args, **kwargs)


# class BpStoreField(fields.Raw, Field):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, data_key="_structure", **kwargs)
#         self.many = many


Str = String
