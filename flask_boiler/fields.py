from google.cloud.firestore import DocumentReference
from marshmallow import fields

from flask_boiler.helpers import RelationshipReference


class Field(fields.Field):

    @property
    def default_value(self):
        return None


class FieldMixin:

    def __init__(self,
                 *args,
                 attribute=None,
                 read_only=None,
                 fieldname_mapper=None,
                 **kwargs):
        """

        :param args:
        :param attribute: obj.attribute
        :param read_only: Sets dump_only to True
        :param fieldname_mapper: for serialization
                f(obj_attribute) = db_document_fieldname
        :param kwargs:
        """

        # attribute
        if read_only is not None or fieldname_mapper is not None:
            if attribute is None:
                raise NotImplementedError("Must specify attribute "
                                          "from kwargs. ")

        # read_only
        if read_only is None:
            read_only = False
        else:
            if read_only:
                if "dump_only" in kwargs or "load_only" in kwargs:
                    raise ValueError("dump_only and or load_only is specified "
                                     "which is not supported "
                                     "when read_only is True. ")


        # # fieldname_mapper and reverse_fieldname_mapper
        # if fieldname_mapper is None and reverse_fieldname_mapper is None:
        #     fieldname_mapper = lambda x: x,
        #     reverse_fieldname_mapper = lambda x: x
        # elif fieldname_mapper is not None and reverse_fieldname_mapper is not None:
        #     if reverse_fieldname_mapper(fieldname_mapper(attribute)) != attribute:
        #         """
        #         Validate mapper
        #         """
        #         a = attribute
        #         b = fieldname_mapper(attribute)
        #         c = reverse_fieldname_mapper(b)
        #         raise ValueError( ("attribute: {} maps to {}, but {} does not "
        #                             "map back to {} and maps to {} instead. ")
        #                             .format(a, b, a, c))
        # else:
        #     raise ValueError("Both fieldname mapper and reverse fieldname "
        #                      "must be specified. ")

        new_kwargs = dict(
            **kwargs
        )

        if attribute is not None:
            new_kwargs["attribute"] = attribute

        if read_only:
            new_kwargs["dump_only"] = True
            new_kwargs["load_only"] = False

        if fieldname_mapper is not None:
            if "dump_to" in kwargs or "load_from" in kwargs:
                raise ValueError("dump_to and or load_from is specified "
                                     "which is not supported "
                                     "when fieldname_mapper is set. ")

            # Firestore document fieldname
            fieldname = fieldname_mapper(attribute)
            new_kwargs["load_from"] = fieldname
            new_kwargs["dump_to"] = fieldname
        else:
            new_kwargs.setdefault("load_from", attribute)
            new_kwargs.setdefault("dump_to", attribute)


        super().__init__(
            *args,
            **new_kwargs
        )

        self.read_only = read_only


class Boolean(FieldMixin, fields.Bool, Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    @property
    def default_value(self):
        return bool()

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Integer(FieldMixin, fields.Integer, Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    @property
    def default_value(self):
        return int()

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Raw(FieldMixin, fields.Raw, Field):

    @property
    def default_value(self):
        return None


class List(FieldMixin, fields.Raw, Field):

    @property
    def default_value(self):
        return list()


class Function(FieldMixin, fields.Function, Field):

    @property
    def default_value(self):
        _x = None

        def fset(x):
            _x = x

        return property(fget=lambda: _x, fset=fset)


class String(FieldMixin, fields.String, Field):

    @property
    def default_value(self):
        return str()


class Nested(FieldMixin, fields.Nested, Field):

    @property
    def default_value(self):
        return None


class Relationship(FieldMixin, fields.Raw, Field):

    def __init__(self, *args, nested=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested = nested

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            raise ValueError
        # Note that AssertionError is not always thrown
        if self.nested:
            return value
        else:
            assert isinstance(value, DocumentReference)
            return RelationshipReference(doc_ref=value,
                                         nested=False)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            raise ValueError
        assert isinstance(value, DocumentReference)
        return RelationshipReference(
            doc_ref=value,
            nested=self.nested,
        )


Str = String
