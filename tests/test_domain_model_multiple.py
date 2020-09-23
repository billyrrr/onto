"""
Some examples are inspired by firestore documentations, some copyright
    conditions of the firestore documentations apply to code on this page.

    https://firebase.google.com/docs/firestore/query-data/queries
"""

import pytest
from google.cloud.firestore import Query, DocumentReference, \
    CollectionReference

from onto.config import Config
from onto.context import Context as CTX

from onto.domain_model import DomainModel
from onto import attrs

# For pytest, DO NOT DELETE
from .fixtures import *

from .utils import _delete_all


class CityM(DomainModel):

    @classmethod
    def _datastore(cls):
        from onto.context import Context as CTX
        return CTX.dbs.leancloud

    city_name = attrs.bproperty()
    country = attrs.bproperty()
    capital = attrs.bproperty()

    class Meta:
        collection_name = "CityM"


class MunicipalityM(CityM):
    pass


class StandardCityM(CityM):
    city_state = attrs.bproperty()
    regions = attrs.bproperty()


@pytest.fixture
def setup_cities(request, CTX):

    def fin():
        for obj in CityM.all():
            obj.delete()

    request.addfinalizer(fin)

    sf = StandardCityM.new(doc_id="SF")

    sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
        'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
    sf.save()

    la = StandardCityM.new(doc_id="LA")
    la.city_name, la.city_state, la.country, la.capital, la.regions = \
        'Los Angeles', 'CA', 'USA', False, ['west_coast', 'socal']
    la.save()

    dc = MunicipalityM.new(doc_id="DC")
    dc.city_name, dc.country, dc.capital = 'Washington D.C.', 'USA', True
    dc.save()

    tok = MunicipalityM.new(doc_id="TOK")
    tok.city_name, tok.country, tok.capital = 'Tokyo', 'Japan', True
    tok.save()

    beijing = MunicipalityM.new(doc_id="BJ")
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
            'obj_type': "MunicipalityM",
            'doc_id': 'DC',
            'doc_ref': 'CityM/DC'
        },
        'San Francisco': {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
            'obj_type': "StandardCityM",
            'doc_id': 'SF',
            'doc_ref': 'CityM/SF'
        },
        'Los Angeles': {
            'cityName': 'Los Angeles',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'socal'],
            'obj_type': "StandardCityM",
            'doc_id': 'LA',
            'doc_ref': 'CityM/LA'
        }

    }

    res_dict = dict()

    for obj in CityM.where(CityM.country=="USA"):
        d = obj.to_dict()
        print(d)
        res_dict[d["cityName"]] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.mark.usefixtures("setup_cities")
def test_subclass_query(CTX):
    assert {city.doc_id for city in CityM.all()} == \
           {'SF', 'LA', 'TOK', 'DC', 'BJ'}
    assert {city.doc_id for city in MunicipalityM.all()} == {'TOK', 'DC', 'BJ'}


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
            'obj_type': "MunicipalityM",
            'doc_id': 'DC',
            'doc_ref': 'CityM/DC'
        },
        'San Francisco': {
            'cityName': 'San Francisco',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'norcal'],
            'obj_type': "StandardCityM",
            'doc_id': 'SF',
            'doc_ref': 'CityM/SF'
        },
        'Los Angeles': {
            'cityName': 'Los Angeles',
            'cityState': 'CA',
            'country': 'USA',
            'capital': False,
            'regions': ['west_coast', 'socal'],
            'obj_type': "StandardCityM",
            'doc_id': 'LA',
            'doc_ref': 'CityM/LA'
        }

    }

    res_dict = dict()

    for obj in CityM.where(country="USA"):
        d = obj.to_dict()
        res_dict[obj.city_name] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.fixture
def setup_and_finalize(request, CTX):

    # Clear City collection before test
    _delete_all(collection_name="CityM", CTX=CTX)

    # Clear City collection after test
    def fin():
        _delete_all(collection_name="CityM", CTX=CTX)

    request.addfinalizer(fin)


@pytest.mark.usefixtures("setup_and_finalize")
def test_from_dict(CTX):
    sf = StandardCityM.from_dict(
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
    sf = StandardCityM.new(doc_id="SF")
    sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
        'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
    assert sf.to_dict() == {
        'cityName': 'San Francisco',
        'cityState': 'CA',
        'country': 'USA',
        'capital': False,
        'regions': ['west_coast', 'norcal'],
        'doc_id': 'SF',
        'doc_ref': 'CityM/SF',
        'obj_type': 'StandardCityM'
    }


@pytest.mark.usefixtures("setup_and_finalize")
def test_from_dict_and_doc_id(CTX):
    sf = StandardCityM.from_dict(
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
    assert sf.doc_ref == "CityM/SF"

    # tear down steps
    sf.delete()
