import pytest

from flask_boiler import utils
from flask_boiler import fields as fb_fields
from marshmallow import fields as marshmallow_fields

from unittest import mock



@pytest.fixture
def mfunc(monkeypatch):
    F = marshmallow_fields.Field
    mfunc = mock.MagicMock(return_value=None)
    monkeypatch.setattr(F, "__init__", mfunc)
    return mfunc


def test_init_read_only(mfunc):

    int_a = fb_fields.Integer(attribute="int_a", read_only=True)

    mfunc.assert_called_once_with(

        attribute = "int_a",

        dump_to="int_a",
        load_from="int_a",

        dump_only=True,
        load_only=False

    )


def test_init_camelize(mfunc):

    int_a = fb_fields.Integer(attribute="int_a",
                    fieldname_mapper=utils.attr_name_to_firestore_key)

    mfunc.assert_called_once_with(

        attribute="int_a",

        dump_to="intA",
        load_from="intA",

    )

