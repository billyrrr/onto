from unittest.mock import patch, call, Mock

import pytest
from google.cloud.firestore_v1 import DocumentReference, Transaction
from testfixtures import compare

from flask_boiler import schema, fields
from flask_boiler.context import Context as CTX
from flask_boiler.config import Config
from flask_boiler.firestore_object import FirestoreObject, \
    ClsFactory, RelationshipStore
from flask_boiler.helpers import RelationshipReference
from flask_boiler.primary_object import PrimaryObject
from flask_boiler.query import run_transaction


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

primary_doc_ref = CTX.db.ref/'primary'/'test_document_0'

class ContainsNestedchema(schema.Schema):
    inner = fields.Relationship(nested=True)

class ContainsNested(FirestoreObject):
    class Meta:
        schema_cls = ContainsNestedchema

    @property
    def doc_ref(self) -> DocumentReference:
        return primary_doc_ref


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

    class ContainsIterSchema(schema.Schema):
        pass

    ContainsIter = ClsFactory.create(
        name="ContainsIter",
        schema=ContainsIterSchema,
        base=FirestoreObject
    )
    doc_ref_1, doc_ref_2 = \
        CTX.db.document("hello/1"), CTX.db.document("hello/2")
    obj = ContainsIter()
    res = obj._import_val(val=[doc_ref_1, doc_ref_2])
    assert res == [doc_ref_1, doc_ref_2]

    res = obj._import_val(val={1: doc_ref_1, 2: doc_ref_2})
    assert res == {1: doc_ref_1, 2: doc_ref_2}


def test_import_nested():

    inner = setup_object(doc_id="inner")

    transaction = CTX.db.transaction()
    doc_ref = inner.doc_ref
    snapshot = doc_ref.get()

    """
    Import document reference from database as object 
    """
    with patch.object(doc_ref, 'get', return_value=snapshot) as mock_method:
        store = RelationshipStore()
        field_deserialized = RelationshipReference(
            nested=True,
            doc_ref=doc_ref,
            obj_type=TestObject
        )
        res = ContainsNested._import_val(val=field_deserialized, _store=store)

        def _get_snapshots(transaction, references):
            return list(
                ref.get()
                for ref in references
            )

        store.refresh(transaction=None, get_snapshots=_get_snapshots)
        assert isinstance(res, TestObject)
        mock_method.assert_called_once()

    """ Import document reference from database without circular reference 
            issues. 
    """
    with patch.object(doc_ref, 'get', return_value=snapshot) as mock_method:
        obj = ContainsNested()
        obj.inner = obj  # An example of circularly referenced object
        obj.save()
        store = RelationshipStore()
        d = {'obj_type': 'ContainsNested', 'doc_ref': 'primary/test_document_0', 'inner': RelationshipReference(nested=True, doc_ref=obj.doc_ref)}
        ContainsNested._import_from_dict(d=d, _store=store)
        assert isinstance(res, TestObject)

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
        store = RelationshipStore()

        res = obj._import_val(
            val=field_deserialized, _store=store, transaction=transaction)
        store.refresh(transaction=None)
        assert isinstance(res, TestObject)
        assert res.transaction == transaction
        mock_method.assert_called_with(
            transaction=transaction
        )

    delete_object(inner.doc_id)


def test_export_nested():

    inner = setup_object(doc_id="inner")

    transaction = CTX.db.transaction()
    doc_ref = inner.doc_ref
    snapshot = doc_ref.get()

    """
    Export value 
    """
    with patch.object(doc_ref, 'set', return_value=None) as mock_method:
        obj = ContainsNested.new(inner=inner)

        field_deserialized = RelationshipReference(
            nested=True,
            obj=obj.inner
        )
        res = obj._export_val(val=field_deserialized)
        assert isinstance(res, DocumentReference)
        mock_method.assert_called_once()

    """
    Set object in relationship reference with transaction
    """
    with patch.object(Transaction, 'set', return_value=None) as mock_method:
        obj = ContainsNested.new(inner=inner, transaction=transaction)

        field_deserialized = RelationshipReference(
            nested=True,
            obj=obj.inner
        )
        res = obj._export_val(
            val=field_deserialized, transaction=transaction)
        assert isinstance(res, DocumentReference)
        mock_method.assert_called_once()

    with patch.object(Transaction, 'set', return_value=None) as mock_method:
        obj = ContainsNested.new(inner=inner, transaction=transaction)
        obj._export_as_dict(transaction=transaction)
        assert mock_method.call_args == call(document_data=inner._export_as_dict(), reference=doc_ref)

    with patch.object(Transaction, 'set', return_value=None) as mock_method:

        @run_transaction
        def do_stuffs(transaction: Transaction):
            global primary_doc_ref
            obj = ContainsNested.new(inner=inner, transaction=transaction, doc_ref=primary_doc_ref)
            obj._export_as_dict(transaction=transaction)

        do_stuffs()

        assert mock_method.call_args == call(document_data=inner._export_as_dict(), reference=doc_ref)

    with patch.object(Transaction, 'set', return_value=None) as mock_method:

        @run_transaction
        def do_stuffs(transaction: Transaction):
            global primary_doc_ref
            obj = ContainsNested.new(inner=inner, transaction=transaction, doc_ref=primary_doc_ref)
            obj._export_as_dict(transaction=transaction)

        do_stuffs()

        assert mock_method.call_args == call(document_data=inner._export_as_dict(), reference=doc_ref)

    with patch.object(Transaction, 'set', return_value=None) as mock_method:

        @run_transaction
        def do_stuffs(transaction: Transaction):
            global primary_doc_ref
            # transaction.set = Mock(return_value=None)
            obj = ContainsNested.new(inner=inner, doc_ref=primary_doc_ref)
            obj._export_as_dict()

        do_stuffs()

        assert Transaction.set.call_args == call(document_data=inner._export_as_dict(), reference=doc_ref)

    """
    Tests that transactions are implicitly passed to referenced objects 
    """

    with patch.object(Transaction, 'set', return_value=None) as mock_method:

        @run_transaction
        def do_stuffs(transaction: Transaction):
            # transaction.set = Mock(return_value=None)
            global primary_doc_ref
            obj = ContainsNested.new(inner=inner, doc_ref=primary_doc_ref)
            obj.save()

        do_stuffs()

        assert mock_method.call_args_list == [
            call(document_data=inner._export_as_dict(), reference=doc_ref),
            call(document_data={'obj_type': 'ContainsNested', 'doc_ref': 'primary/test_document_0', 'inner': doc_ref}, reference=primary_doc_ref)
        ]

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
        "nestedRef": CTX.db.ref/"TestObject"/"testObjId1"
    }

    master_obj.delete()
    CTX.db.delete(reference=CTX.db.ref/"TestObject"/"testObjId1")


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

    assert master_obj._export_as_dict() == {
        'doc_id': 'masterObjIdNested1',
        'doc_ref': 'MasterObjectNested/masterObjIdNested1',
        'obj_type': 'MasterObjectNested',
        "nestedObj": referenced_obj.doc_ref
    }

    master_obj.save()

    assert CTX.db.ref/"TestObject"/"testObjId3".get().to_dict() == \
           {
               "intA": 1,
               "intB": 2,
               "obj_type": "TestObject",
               'doc_id': 'testObjId3',
               'doc_ref': "TestObject/testObjId3"
           }

    master_obj.delete()
    CTX.db.delete(reference=CTX.db.ref/"TestObject"/"testObjId3")


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
