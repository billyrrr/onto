import pytest
from testfixtures import compare

from src import schema, fields


def test__get_field_vars():
    """
    Tests that _get_field_vars returns a dictionary of expected Field objects.
    """

    class TestObject:

        def __init__(self):
            self.int_a = 0
            self.int_b = 0

    obj = TestObject()

    field_vars = schema._get_field_vars(vars(obj))
    print(field_vars)

    def field_comparator(x, y, _):
        """
        Test fixture for comparing two fields.Field objects
        """
        if x.load_from != y.load_from:
            return "x != y since x.load_from: {} != y.load_from: {}".format(
                x.load_from, y.load_from
            )

    compare(

        field_vars, {
            "int_a": fields.Integer(load_from="intA"),
            "int_b": fields.Integer(load_from="intB"),
        }, comparers={fields.Field: field_comparator}

    )


def test_set_attr():
    """
    Tests that generate_schema returns a schema that has the ability to
        set instance variables based on keys of different format in the
        dictionary provided in schema.load(d)
    """

    class TestObject:

        def __init__(self):
            self.int_a = 0
            self.int_b = 0

    obj = TestObject()
    s = schema.generate_schema(obj)

    s.load({
        "intA": 1,
        "intB": 2
    })

    assert obj.int_a == 1
    assert obj.int_b == 2

    # TODO: test that no extraneous attributes are set


def test_conversion():
    """
    Tests that "camelCase" key used in Firestore converts to "snake_case"
        target instance variable names.
    """

    res = schema.firestore_key_to_attr_name("intA")
    assert res == "int_a"

    r_res = schema.attr_name_to_firestore_key("int_a")
    assert r_res == "intA"
