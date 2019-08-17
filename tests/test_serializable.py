from src import serializable
from src import view_model, schema


def test__additional_fields():
    class ModelA(view_model.ViewModel, serializable_fields=["int_a"]):
        int_a = 0

    class ModelAA(ModelA, serializable_fields=["int_a", "int_aa"]):
        int_aa = 0

    assert ModelA._fields == ["int_a"]
    assert ModelAA._fields == ["int_a", "int_aa"]


def test_infer_fields():
    class ModelA(view_model.ViewModel, serializable_fields=None):
        int_a = 0

    assert ModelA._infer_fields() == ["int_a"]


def test_infer_property_fields():
    class ModelAp(view_model.ViewModel, serializable_fields=None):
        int_a = 0

        @property
        def some_property(self):
            return 0

    assert ModelAp._infer_fields() == ["int_a", "some_property"]


def test_singleton_schema():
    """
    Tests that many instances of the same class is initialized
        with one same schema.
    """

    class ModelA(view_model.ViewModel):

        def __init__(self):
            self.int_a = 0

    a = ModelA()
    assert a.schema_obj

    a1, a2 = ModelA(), ModelA()
    assert a1.schema_obj is a2.schema_obj


def test_generate_schema():
    class ModelA(serializable.Serializable,
                 serializable_fields=["int_a", "int_b"]):

        def __init__(self):
            super().__init__()
            self.int_a = 0
            self.int_b = 0

    a = ModelA()


def test_multiple_inheritance():
    class ModelA(view_model.ViewModel):

        def __init__(self):
            super().__init__()
            self.int_a = 0

    class ModelB(view_model.ViewModel):

        def __init__(self):
            super().__init__()
            self.int_b = 1

    class ModelAB(ModelA, ModelB):

        def __init__(self):
            super().__init__()

    ab = ModelAB()
    ab.int_a = 1
    ab.int_b = 2

    assert ab.int_a == 1
    assert ab.int_b == 2

    assert ab._export_as_dict() == {
        "intA": 1,
        "intB": 2
    }


def test__export_as_dict():
    class ModelASchema(schema.Schema):
        int_a = schema.fields.Integer(load_from="intA", dump_to="intA")
        int_b = schema.fields.Integer(load_from="intB", dump_to="intB")

    class ModelA(serializable.Serializable,
                 serializable_fields=["int_a", "int_b"]):
        _schema_cls = ModelASchema

        def __init__(self):
            super().__init__()
            self.int_a = 0
            self.int_b = 0

    a = ModelA()
    a.int_a = 1
    a.int_b = 2

    assert a._export_as_dict() == {
        "intA": 1,
        "intB": 2
    }
