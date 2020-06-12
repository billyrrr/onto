import functools
from _weakref import ProxyType
from collections import UserDict, UserList

import pytest

from flask_boiler import utils, fields, attrs
from flask_boiler import schema as fb_schema
from flask_boiler import fields as fb_fields
from marshmallow import fields as marshmallow_fields, schema

from unittest import mock

from flask_boiler.common import _NA
from flask_boiler.domain_model import DomainModel
from flask_boiler.factory import ClsFactory
from flask_boiler.firestore_object import FirestoreObject, \
    _nest_relationship_import, RelationshipStore
from flask_boiler.helpers import RelationshipReference
from flask_boiler.models.base import Serializable
from flask_boiler.snapshot_container import SnapshotContainer

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


def test_something():

    class MyDescriptor:

        def __init__(self):
            self._val = None

        def __get__(self, obj, objtype):
            return self._val

        def __set__(self, obj, val):
            self._val = val

    class Owner:

        my = MyDescriptor()

    instance = Owner()
    instance.my = "hi"
    assert instance.my == "hi"

    d = dict(a=MyDescriptor())
    assert d['a'] == "hello"


def test_wrapper():

    class Retriever:

        def __set_name__(self, owner, name):
            self.parent = owner
            self.name = name

        def __set__(self, instance, value):
            raise TypeError("Reassigning an iterable wrapper is not allowed")

        def __get__(self, instance, owner):
            import weakref

            return weakref.proxy(instance.original)

    class Dict(UserDict):
        pass

    class List(UserList):
        pass

    _original = List([1, 2])

    class K:

        proxy = Retriever()

        def __init__(self):
            self.original = _original

    k = K()

    assert k.proxy.index(1) == 0
    assert not hasattr(k.proxy, "non_existent")

    _internal_list = k.proxy
    try:
        k.proxy = list()
    except TypeError as e:
        assert True
    else:
        assert False

    class M:
        pass

    m = M()
    m.original = k.original

    print(m.original)

    assert k.proxy[0] == 1
    assert len(m.original) == 2


def test_proxy(CTX):

    class A(DomainModel):
        foo = attrs.bproperty()

    doc_ref = CTX.db.document('A/a')
    doc_ref.set(dict(foo='bar'))

    s = RelationshipStore()

    from google.cloud.firestore import transactional
    @transactional
    def execute(transaction):
        rr = RelationshipReference(doc_ref=doc_ref, obj_type=A)
        a = _nest_relationship_import(rr, store=s)

        s.refresh(transaction=transaction)

        assert a.foo == 'bar'
        assert isinstance(a, A)

    execute(transaction=CTX.db.transaction())

    def execute_no_transaction():
        rr = RelationshipReference(doc_ref=doc_ref, obj_type=A)
        a = _nest_relationship_import(rr, store=s)

        s.refresh(transaction=None)

        assert a.foo == 'bar'
        assert isinstance(a, A)

    execute_no_transaction()

def test_local_time():
    from flask_boiler.fields import local_time_from_timestamp, timestamp_from_local_time
    local_time_str = local_time_from_timestamp(1545062400)
    assert local_time_str == "2018-12-17T08:00:00"
    local_time_timestamp = timestamp_from_local_time("2018-12-17T08:00:00")
    assert local_time_timestamp == 1545062400


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

