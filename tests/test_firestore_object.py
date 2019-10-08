import pytest
from testfixtures import compare

from flask_boiler import schema, fields
from flask_boiler.context import Context as CTX
from flask_boiler.config import Config
from flask_boiler.firestore_object import FirestoreObject, \
    FirestoreObjectClsFactory
from flask_boiler.primary_object import PrimaryObject

config = Config(
    app_name="flask-boiler-testing",
    debug=True,
    testing=True,
    certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
)
CTX.read(config)
assert CTX.firebase_app.project_id == "flask-boiler-testing"


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


def test_relationship_not_nested():
    referenced_obj = TestObject.create(doc_id="testObjId1")

    # Assigns value to the newly created object
    referenced_obj.int_a = 1
    referenced_obj.int_b = 2

    # Saves to firestore "TestObject/testObjId1"
    referenced_obj.save()

    class MasterObjectSchema(schema.Schema):
        # Describes how obj.int_a is read from and stored to a document in firestore
        nested_ref = fields.Relationship(nested=False)

    MasterObject = FirestoreObjectClsFactory.create(
        name="MasterObject",
        schema=MasterObjectSchema,
        base=PrimaryObject
    )

    master_obj = MasterObject.create(doc_id="masterObjId1")
    master_obj.nested_ref = referenced_obj.doc_ref
    assert master_obj._export_as_dict() == {
        'doc_id': 'masterObjId1',
        'doc_ref': 'MasterObject/masterObjId1',
        'obj_type': 'MasterObject',
        "nestedRef": CTX.db.document("TestObject/testObjId1")
    }

    master_obj.delete()
    CTX.db.document("TestObject/testObjId1").delete()


def test_relationship_nested():
    referenced_obj = TestObject.create(doc_id="testObjId3")

    # Assigns value to the newly created object
    referenced_obj.int_a = 1
    referenced_obj.int_b = 2

    class MasterObjectSchemaNested(schema.Schema):
        # Describes how obj.int_a is read from and stored to a document in firestore
        nested_obj = fields.Relationship(nested=True)

    MasterObjectNested = FirestoreObjectClsFactory.create(
        name="MasterObjectNested",
        schema=MasterObjectSchemaNested,
        base=PrimaryObject
    )

    master_obj = MasterObjectNested.create(doc_id="masterObjIdNested1")
    master_obj.nested_obj = referenced_obj

    assert master_obj._export_as_dict(to_save=True) == {
        'doc_id': 'masterObjIdNested1',
        'doc_ref': 'MasterObjectNested/masterObjIdNested1',
        'obj_type': 'MasterObjectNested',
        "nestedObj": referenced_obj.doc_ref
    }

    master_obj.save()

    assert CTX.db.document("TestObject/testObjId3").get().to_dict() == \
           {
               "intA": 1,
               "intB": 2,
               "obj_type": "TestObject",
               'doc_id': 'testObjId3',
               'doc_ref': "TestObject/testObjId3"
           }

    master_obj.delete()
    CTX.db.document("TestObject/testObjId3").delete()


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
