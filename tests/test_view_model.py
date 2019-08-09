import pytest
from marshmallow import Schema
from src import view_model
from src import fields


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
        fields = ["int_a"]
        int_a = 0

    a = ModelA()
    assert a._schema

    a1, a2 = ModelA(), ModelA()
    assert a1._schema is a2._schema


def test_multiple_inheritance():

    class ModelA(view_model.ViewModel):
        int_a = 0

    class ModelB(view_model.ViewModel):
        int_b = 1

    class ModelAB(ModelA, ModelB):
        pass

    ab = ModelAB()
    ab.int_a = 1
    ab.int_b = 2

    assert ab.int_a == 1
    assert ab.int_b == 2

    assert ab.to_dict() == {
        "int_a": 1,
        "int_b": 2
    }

