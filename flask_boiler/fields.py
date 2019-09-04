from marshmallow import fields


class Field(fields.Field):

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
        if attribute is None:
            raise NotImplementedError("Must specify attribute from kwargs. ")

        # read_only
        if read_only is None:
            read_only = False
        else:
            if read_only:
                if "dump_only" in kwargs or "read_only" in kwargs:
                    raise ValueError("dump_only and or read_only is specified "
                                     "which is not supported "
                                     "when read_only is True. ")

        if fieldname_mapper is None:
            fieldname_mapper = lambda x: x

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

        # Firestore document fieldname
        fieldname = fieldname_mapper(attribute)
        new_kwargs["load_from"] = fieldname
        new_kwargs["dump_to"] = fieldname

        super().__init__(
            *args,
            **new_kwargs
        )

        self.read_only = read_only

    @property
    def default_value(self):
        return None


class Boolean(fields.Bool, Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return bool()

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Integer(fields.Integer, Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return int()

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Raw(fields.Raw, Field):

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return None


class List(fields.Raw, Field):

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return list()


class Function(fields.Function, Field):

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        _x = None

        def fset(x):
            _x = x

        return property(fget=lambda: _x, fset=fset)


class String(fields.String, Field):

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return str()


class Nested(fields.Nested, Field):

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

    @property
    def default_value(self):
        return None


Str = String
