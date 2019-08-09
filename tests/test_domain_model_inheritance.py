import pytest
from src import domain_model


def test_inheritance():

    class ModelA(domain_model.DomainModel):

        def __init__(self, doc_id=None):
            super().__init__(doc_id=doc_id)
            self.int_a = 0
            self.int_b = 0

    a = ModelA()
    a.int_a = 1
    a.int_b = 2

    assert a._export_as_dict() == {
        "int_a": 1,
        "int_b": 2
    }

