from marshmallow import fields


class Field(fields.Field):

    def __init__(self, *args, read_only=False, **kwargs):
        self.read_only = read_only
        if read_only:
            super().__init__(
                *args,
                dump_only=True,
                **kwargs
            )
        else:
            super().__init__(
                *args,
                **kwargs
            )

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

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Integer(fields.Integer, Field):
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


class Raw(fields.Raw, Field):

    @property
    def default_value(self):
        return None


class List(fields.Raw, Field):

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


Str = String
