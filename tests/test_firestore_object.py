import pytest
from testfixtures import compare

from src import schema, fields
from src.context import Context as CTX
from src.config import Config
from src.firestore_object import FirestoreObject, PrimaryObject


def test_create_obj():
    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )
    CTX.read(config)
    assert CTX.firebase_app.project_id == "gravitate-dive-testing"

    # Creates a schema for serializing and deserializing to firestore database
    class TestObjectSchema(schema.Schema):
        # Describes how obj.int_a is read from and stored to a document in firestore
        int_a = fields.Raw(
            load_from="intA",
            # reads obj.int_a from firestore document field "intA"
            dump_to="intA"
            # stores the value of obj.int_a to firestore document field "intA"
        )
        int_b = fields.Raw(load_from="intB", dump_to="intB")

    # Declares the object
    class TestObject(PrimaryObject):
        _schema_cls = TestObjectSchema

        def __init__(self, doc_id=None):
            super().__init__(doc_id=doc_id)

            # Initializes default values of your instance variables
            self.int_a = 0
            self.int_b = 0

    # Creates an object with default values with reference: "TestObject/testObjId1"
    #   (but not saved to database)
    obj = TestObject.create(doc_id="testObjId1")
    assert obj.doc_id == "testObjId1"
    assert obj.collection_name == "TestObject"

    # Assigns value to the newly created object
    obj.int_a = 1
    obj.int_b = 2

    # Saves to firestore "TestObject/testObjId1"
    obj.save()

    # Gets the object from firestore "TestObject/testObjId1"
    retrieved_obj = TestObject.get(doc_id="testObjId1")

    # Access values of the object retrieved
    assert retrieved_obj.int_a == 1
    assert retrieved_obj.int_b == 2

    # Deletes the object from firestore "TestObject/testObjId1"
    retrieved_obj.delete()
