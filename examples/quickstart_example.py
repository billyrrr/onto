from onto.context import Context as CTX
from onto.config import Config

from onto import schema, fields, utils

from onto.firestore_object import FirestoreObject, \
    ClsFactory
from onto.primary_object import PrimaryObject


if not CTX._ready:
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
    int_a = fields.Raw()
    int_b = fields.Raw()


# Declares the object
TestObject = ClsFactory.create(
    name="TestObject",
    schema=TestObjectSchema,
    base=PrimaryObject
)

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
