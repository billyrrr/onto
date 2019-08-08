from src import fields
from marshmallow import Schema


def generate_schema(obj) -> Schema:
    """
    Generates
    :param obj:
    :return:
    """
    class TempSchema(Schema):
        int_a = fields.Integer()
        int_b = fields.Integer()
    return TempSchema()
