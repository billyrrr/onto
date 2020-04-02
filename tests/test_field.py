import pytest

from flask_boiler import utils, fields
from flask_boiler import schema as fb_schema
from flask_boiler import fields as fb_fields
from marshmallow import fields as marshmallow_fields, schema

from unittest import mock

from flask_boiler.factory import ClsFactory
from flask_boiler.firestore_object import FirestoreObject
from flask_boiler.helpers import RelationshipReference

from .fixtures import CTX


@pytest.fixture
def mfunc(monkeypatch):
    F = marshmallow_fields.Field
    mfunc = mock.MagicMock(return_value=None)
    monkeypatch.setattr(F, "__init__", mfunc)
    return mfunc


def test_init_read_only():

    int_a_field = marshmallow_fields.Integer(dump_only=True)

    class TrivialSchema(fb_schema.Schema):

        int_a = int_a_field

    assert int_a_field.dump_only


def test_relationship_many(CTX):

    class ContainsIterableSchema(schema.Schema):
        the_iterable = fields.Relationship(nested=False, many=True)

    fd = ContainsIterableSchema().fields["the_iterable"]

    doc_ref_1, doc_ref_2 = \
        CTX.db.document("hello/1"), CTX.db.document("hello/2")

    res = fd.deserialize(value=[doc_ref_1, doc_ref_2])

    assert res == [RelationshipReference(nested=False, doc_ref=doc_ref_1),
                   RelationshipReference(nested=False, doc_ref=doc_ref_2)]

    res = fd.deserialize(value={1: doc_ref_1, 2: doc_ref_2})

    assert res == {1: RelationshipReference(nested=False, doc_ref=doc_ref_1),
                   2: RelationshipReference(nested=False, doc_ref=doc_ref_2)}

    ContainsIterable = ClsFactory.create(
        "ContainsIterable",
        schema=ContainsIterableSchema,
        base=FirestoreObject
    )

    obj = ContainsIterable.new(the_iterable=[doc_ref_1, doc_ref_2])
    res = fd.serialize(obj=obj, attr="the_iterable")
    assert res == [RelationshipReference(nested=False, doc_ref=doc_ref_1),
                   RelationshipReference(nested=False, doc_ref=doc_ref_2)]

    obj = ContainsIterable.new(the_iterable={1: doc_ref_1, 2: doc_ref_2})
    res = fd.serialize(obj=obj, attr="the_iterable")
    assert res == {1: RelationshipReference(nested=False, doc_ref=doc_ref_1),
                   2: RelationshipReference(nested=False, doc_ref=doc_ref_2)}


# def test_projected():
#
#     from flask_boiler.schema import Schema
#     from flask_boiler import fields
#
#     class ArtistSchema(Schema):
#         id = fields.Integer()
#         name = fields.String()
#
#     class AlbumSchema(Schema):
#         id = fields.Projected(ArtistSchema, 'artist')
#
#     in_data = {'id': 42}
#     loaded = AlbumSchema().load(in_data)  # => {'artist': {'id': 42}}
#     print(loaded)
#     dumped = AlbumSchema().dump(loaded)  # => {'id': 42}
#     print(dumped)

#
# def test_init_camelize():
#
#     int_a = fb_fields.Integer(attribute="int_a",
#                     fieldname_mapper=utils.attr_name_to_firestore_key)
#
#     mfunc.assert_called_once_with(
#
#         attribute="int_a",
#
#         dump_to="intA",
#         load_from="intA",
#
#     )

