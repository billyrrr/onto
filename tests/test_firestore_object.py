import pytest
from testfixtures import compare

from flask_boiler import schema, fields
from flask_boiler.context import Context as CTX
from flask_boiler.config import Config
from flask_boiler.firestore_object import FirestoreObject, PrimaryObject, \
    FirestoreObjectClsFactory

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
        # load_from="intA",
        # reads obj.int_a from firestore document field "intA"
        # dump_to="intA"
        # stores the value of obj.int_a to firestore document field "intA"
    )
    int_b = fields.Raw(
        # load_from="intB", dump_to="intB"
                       )


# Declares the object
TestObject = FirestoreObjectClsFactory.create(
    name="TestObject",
    schema=TestObjectSchema,
    base=PrimaryObject
)


def test_create_obj():

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


def setup_object(doc_id):

    # Creates an object with default values with reference: "TestObject/testObjId1"
    #   (but not saved to database)
    obj = TestObject.create(doc_id=doc_id)
    assert obj.doc_id == doc_id
    assert obj.collection_name == "TestObject"

    # Assigns value to the newly created object
    obj.int_a = 1
    obj.int_b = 2

    # Saves to firestore "TestObject/testObjId1"
    obj.save()


def delete_object(doc_id):

    # Creates an object with default values with reference: "TestObject/testObjId1"
    #   (but not saved to database)
    obj = TestObject.create(doc_id=doc_id)

    # Deletes "TestObject/testObjId1"
    obj.delete()


def test_stream_objects():

    setup_object(doc_id="testObjId1")
    setup_object(doc_id="testObjId2")

    for obj in TestObject.all():
        assert obj.doc_id in {"testObjId1", "testObjId2"}
        assert obj.to_dict().items() >= {
            "intA": 1,
            "intB": 2,
            "obj_type": "TestObject"
        }.items()

    for obj in TestObject.all():
        obj.delete()
