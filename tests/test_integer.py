import pytest
from marshmallow import Schema
from onto import fields


def test_basic_schema():

    class BasicSchema(Schema):
        integer_field = fields.Integer()

    class BasicObj:

        def __init__(self):
            self.integer_field = 0

    bs = BasicSchema()
    bo = BasicObj()
    bo.integer_field = 1

    d = bs.dump(bo)
    assert d == {
        "integer_field": 1
    }


