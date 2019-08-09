from marshmallow import fields

Field = fields.Field

class Boolean(Field):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value


class Integer(Field):
    """Field that serializes to an integer and deserializes
            to an integer.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        return value
