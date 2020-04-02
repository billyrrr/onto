from unittest.mock import patch

import pytest
from google.cloud.firestore_v1 import DocumentReference
from testfixtures import compare

from flask_boiler import schema, fields
from flask_boiler.context import Context as CTX
from flask_boiler.config import Config
from flask_boiler.firestore_object import FirestoreObject, \
    ClsFactory
from flask_boiler.helpers import RelationshipReference
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
class TestObject(PrimaryObject):
    _schema_cls = TestObjectSchema

# TestObject = ClsFactory.new(
#     name="TestObject",
#     schema=TestObjectSchema,
#     base=PrimaryObject
# )


def test_create_obj():

    # Creates an object with default values with reference: "TestObject/testObjId1"
    #   (but not saved to database)
    obj = TestObject.new(doc_id="testObjId1")
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


def test_import_iterable():

    class ContainsIterchema(schema.Schema):
        pass

    ContainsIter = ClsFactory.create(
        name="ContainsIter",
        schema=ContainsIterchema,
        base=FirestoreObject
    )
    doc_ref_1, doc_ref_2 = \
        CTX.db.document("hello/1"), CTX.db.document("hello/2")
    obj = ContainsIter()
    res = obj._import_val(val=[doc_ref_1, doc_ref_2], to_get=False)
    assert res == [doc_ref_1, doc_ref_2]

    res = obj._import_val(val={1: doc_ref_1, 2: doc_ref_2}, to_get=False)
    assert res == {1: doc_ref_1, 2: doc_ref_2}


def test_import_nested():

    inner = setup_object(doc_id="inner")

    class ContainsNestedchema(schema.Schema):
        pass

    ContainsNested = ClsFactory.create(
        name="ContainsNested",
        schema=ContainsNestedchema,
        base=FirestoreObject
    )

    transaction = CTX.db.transaction()
    doc_ref = inner.doc_ref
    snapshot = doc_ref.get()

    """
    Import document reference from database as object 
    """
    with patch.object(doc_ref, 'get', return_value=snapshot) as mock_method:
        obj = ContainsNested()

        field_deserialized = RelationshipReference(
            nested=True,
            doc_ref=doc_ref
        )
        res = obj._import_val(val=field_deserialized, to_get=True)
        assert isinstance(res, TestObject)
        mock_method.assert_called_once()

    """ (Default behavior)
        Import document reference from database as reference to 
            avoid circular reference issues. 
    """
    with patch.object(doc_ref, 'get', return_value=snapshot) as mock_method:
        obj = ContainsNested()

        field_deserialized = RelationshipReference(
            nested=True,
            doc_ref=doc_ref
        )
        # to_get is set to False when importing a nested object in a
        #     nested object to avoid circular reference.
        res = obj._import_val(val=field_deserialized, to_get=False)
        assert isinstance(res, DocumentReference)
        mock_method.assert_not_called()

    """
    Import document reference from database as object that 
        has transaction 
    """
    with patch.object(doc_ref, 'get', return_value=snapshot) as mock_method:
        obj = ContainsNested(transaction=transaction)

        field_deserialized = RelationshipReference(
            nested=True,
            doc_ref=doc_ref
        )
        res = obj._import_val(
            val=field_deserialized, to_get=True, transaction=transaction)
        assert isinstance(res, TestObject)
        assert res.transaction == transaction
        mock_method.assert_called_with(
            transaction=transaction
        )


    delete_object(inner.doc_id)


def test_relationship_not_nested():
    referenced_obj = TestObject.new(doc_id="testObjId1")

    # Assigns value to the newly created object
    referenced_obj.int_a = 1
    referenced_obj.int_b = 2

    # Saves to firestore "TestObject/testObjId1"
    referenced_obj.save()

    class MasterObjectSchema(schema.Schema):
        # Describes how obj.int_a is read from and stored to a document in firestore
        nested_ref = fields.Relationship(nested=False)

    MasterObject = ClsFactory.create(
        name="MasterObject",
        schema=MasterObjectSchema,
        base=PrimaryObject
    )

    master_obj = MasterObject.new(doc_id="masterObjId1")
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
    referenced_obj = TestObject.new(doc_id="testObjId3")

    # Assigns value to the newly created object
    referenced_obj.int_a = 1
    referenced_obj.int_b = 2

    class MasterObjectSchemaNested(schema.Schema):
        # Describes how obj.int_a is read from and stored to a document in firestore
        nested_obj = fields.Relationship(nested=True)

    MasterObjectNested = ClsFactory.create(
        name="MasterObjectNested",
        schema=MasterObjectSchemaNested,
        base=PrimaryObject
    )

    master_obj = MasterObjectNested.new(doc_id="masterObjIdNested1")
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
    obj = TestObject.new(doc_id=doc_id)
    assert obj.doc_id == doc_id
    assert obj.collection_name == "TestObject"

    # Assigns value to the newly created object
    obj.int_a = 1
    obj.int_b = 2

    # Saves to firestore "TestObject/testObjId1"
    obj.save()

    return obj


def delete_object(doc_id):

    # Creates an object with default values with reference: "TestObject/testObjId1"
    #   (but not saved to database)
    obj = TestObject.new(doc_id=doc_id)

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
