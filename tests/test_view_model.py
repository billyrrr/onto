import pytest
from marshmallow import Schema
from src import view_model
from src import fields


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

