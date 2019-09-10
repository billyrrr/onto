"""
Some examples are inspired by firestore documentations, some copyright
    conditions of the firestore documentations apply to code on this page.

    https://firebase.google.com/docs/firestore/query-data/queries
"""

import pytest
from google.cloud.firestore import Query, DocumentReference, \
    CollectionReference

from flask_boiler.config import Config
from flask_boiler.context import Context as CTX

from flask_boiler.firestore_object import FirestoreObjectClsFactory
from flask_boiler.domain_model import DomainModel
from flask_boiler.schema import Schema
from flask_boiler import fields

# For pytest, DO NOT DELETE
from .fixtures import *

from .utils import _delete_all


class CitySchema(Schema):
    city_name = fields.Raw()

    country = fields.Raw()
    capital = fields.Raw()


class MunicipalitySchema(CitySchema):
    pass


class StandardCitySchema(CitySchema):
    city_state = fields.Raw()
    regions = fields.Raw(many=True)


class CityBase(DomainModel):
    _collection_name = "City"


Municipality = FirestoreObjectClsFactory.create(
    name="Municipality",
    schema=MunicipalitySchema,
    base=CityBase,
)


StandardCity = FirestoreObjectClsFactory.create(
    name="StandardCity",
    schema=StandardCitySchema,
    base=CityBase
)


@pytest.fixture
def setup_cities(request, CTX):

    def fin():
        _delete_all(collection_name="City", CTX=CTX)

    request.addfinalizer(fin)

    sf = StandardCity.create(doc_id="SF")
    sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
        'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
    sf.save()

    la = StandardCity.create(doc_id="LA")
    la.city_name, la.city_state, la.country, la.capital, la.regions = \
        'Los Angeles', 'CA', 'USA', False, ['west_coast', 'socal']
    la.save()

    dc = Municipality.create(doc_id="DC")
    dc.city_name, dc.country, dc.capital = 'Washington D.C.', 'USA', True
    dc.save()

    tok = Municipality.create(doc_id="TOK")
    tok.city_name, tok.country, tok.capital = 'Tokyo', 'Japan', True
    tok.save()

    beijing = Municipality.create(doc_id="BJ")
    beijing.city_name, beijing.country, beijing.capital = \
        'Beijing', 'China', True
    beijing.save()


@pytest.mark.usefixtures("setup_cities")
def test_subclass_same_collection(CTX):
    """
    Tests that subclasses of a class can be stored in the same collection.
    :return:
    """

    expected_dict = {
        'Washington D.C.': {
            'cityName': 'Washington D.C.',
            'country': 'USA',
            'capital': True,
            'obj_type': "Municipality",
            'doc_id': 'DC',
            'doc_ref': 'City/DC'
        },
        'San Francisco': {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
            'obj_type': "StandardCity",
            'doc_id': 'SF',
            'doc_ref': 'City/SF'
        },
        'Los Angeles': {
            'cityName': 'Los Angeles',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'socal'],
            'obj_type': "StandardCity",
            'doc_id': 'LA',
            'doc_ref': 'City/LA'
        }

    }

    res_dict = dict()

    for obj in CityBase.where("country", "==", "USA"):
        d = obj.to_dict()
        # print(d)
        res_dict[d["cityName"]] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.mark.usefixtures("setup_cities")
def test_where_with_kwargs(CTX):
    """
    Tests that subclasses of a class can be stored in the same collection.
    :return:
    """

    expected_dict = {
        'Washington D.C.': {
            'cityName': 'Washington D.C.',
            'country': 'USA',
            'capital': True,
            'obj_type': "Municipality",
            'doc_id': 'DC',
            'doc_ref': 'City/DC'
        },
        'San Francisco': {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
            'obj_type': "StandardCity",
            'doc_id': 'SF',
            'doc_ref': 'City/SF'
        },
        'Los Angeles': {
            'cityName': 'Los Angeles',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'socal'],
            'obj_type': "StandardCity",
            'doc_id': 'LA',
            'doc_ref': 'City/LA'
        }

    }

    res_dict = dict()

    for obj in CityBase.where(country="USA"):
        d = obj.to_dict()
        res_dict[obj.city_name] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.fixture
def setup_and_finalize(request, CTX):

    # Clear City collection before test
    _delete_all(collection_name="City", CTX=CTX)

    # Clear City collection after test
    def fin():
        _delete_all(collection_name="City", CTX=CTX)

    request.addfinalizer(fin)


@pytest.mark.usefixtures("setup_and_finalize")
def test_from_dict(CTX):
    sf = StandardCity.from_dict(
        {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
        },
    )
    assert sf.city_state == "CA"
    sf.save()


def test_to_dict(CTX):
    sf = StandardCity.create(doc_id="SF")
    sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
        'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
    assert sf.to_dict() == {
        'cityName': 'San Francisco',
        'cityState': 'CA',
        'country': 'USA',
        'capital': False,
        'regions': ['west_coast', 'norcal'],
        'doc_id': 'SF',
        'doc_ref': 'City/SF',
        'obj_type': 'StandardCity'
    }


@pytest.mark.usefixtures("setup_and_finalize")
def test_from_dict_and_doc_id(CTX):
    sf = StandardCity.from_dict(
        {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
        }, doc_id="SF"
    )

    sf.save()

    assert sf.doc_id == "SF"
    assert sf.doc_ref.path == "City/SF"

    # tear down steps
    sf.delete()

