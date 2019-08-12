import pytest
from testfixtures import compare

from src import schema, fields
from src.context import Context as CTX
from src.config import Config
from src.firestore_object import FirestoreObject


def test_create_obj():
    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )
    CTX.read(config)
    assert CTX.firebase_app.project_id == "gravitate-dive-testing"

    class TestObjectSchema(schema.Schema):
        int_a = fields.Raw(load_from="intA", dump_to="intA")
        int_b = fields.Raw(load_from="intB", dump_to="intB")

    class TestObject(FirestoreObject):

        _schema = TestObjectSchema()

        def __init__(self, doc_id=None):
            super().__init__(doc_id=doc_id)
            self.int_a = 0
            self.int_b = 0

    obj = TestObject.create(doc_id="testObjId1")
    obj.int_a = 1
    obj.int_b = 2
    assert obj.doc_id == "testObjId1"
    assert obj.collection_name == "TestObject"
    obj.save()

    retrieved_obj = TestObject.get(doc_id="testObjId1")
    assert retrieved_obj.int_a == 1
    assert retrieved_obj.int_b == 2

    retrieved_obj.delete()
