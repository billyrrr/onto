import pytest

from flask_boiler import utils
from flask_boiler import schema as fb_schema
from flask_boiler import fields as fb_fields
from marshmallow import fields as marshmallow_fields

from unittest import mock


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

