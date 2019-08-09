from src import schema


def test_set_attr():

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

    res = schema.firestore_key_to_attr_name("intA")
    assert res == "int_a"
