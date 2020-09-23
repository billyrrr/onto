"""
Some examples are inspired by firestore documentations, some copyright
    conditions of the firestore documentations apply to code on this page.

    https://firebase.google.com/docs/firestore/query-data/queries
"""

import pytest

from onto.domain_model import DomainModel
from onto.mapper.schema import Schema, BasicSchema
from onto import fields, collection_mixin, attrs

# For pytest, DO NOT DELETE
from onto.primary_object import PrimaryObjectSchema
from .fixtures import *

from .utils import _delete_all

from examples.city.models import City, Municipality, StandardCity


@pytest.fixture
def setup_cities(request, CTX):
    def fin():
        _delete_all(collection_name="City", CTX=CTX)

    request.addfinalizer(fin)

    sf = StandardCity.new(doc_id="SF")
    sf.city_name, sf.city_state, sf.country, sf.capital, sf.regions = \
        'San Francisco', 'CA', 'USA', False, ['west_coast', 'norcal']
    sf.save()

    la = StandardCity.new(doc_id="LA")
    la.city_name, la.city_state, la.country, la.capital, la.regions = \
        'Los Angeles', 'CA', 'USA', False, ['west_coast', 'socal']
    la.save()

    dc = Municipality.new(doc_id="DC")
    dc.city_name, dc.country, dc.capital = 'Washington D.C.', 'USA', True
    dc.save()

    tok = Municipality.new(doc_id="TOK")
    tok.city_name, tok.country, tok.capital = 'Tokyo', 'Japan', True
    tok.save()

    beijing = Municipality.new(doc_id="BJ")
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

    for obj in City.where("country", "==", "USA"):
        d = obj.to_dict()
        print(d)
        res_dict[d["cityName"]] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.mark.usefixtures("setup_cities")
def test_subclass_query(CTX):
    assert {city.doc_id for city in City.all()} == \
           {'SF', 'LA', 'TOK', 'DC', 'BJ'}
    assert {city.doc_id for city in Municipality.all()} == {'TOK', 'DC', 'BJ'}


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

    for obj in City.where(country="USA"):
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
    sf = StandardCity.new(doc_id="SF")
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
    assert sf.doc_ref == "City/SF"

    # tear down steps
    sf.delete()


def test_customized_reserved_fields_domain_model(CTX):
    """ Tests deserialization of domain model that has no default fields:
            doc_ref, doc_id, obj_type

    :return:
    """

    class OrderComplex(DomainModel):
        """
        Example of a use case of overriding obj_type field to customize
            the data_key for saving and reading obj_type
        """

        class _schema_cls(PrimaryObjectSchema):
            obj_type = fields.ObjectTypeField(data_key="_object_type")

            status = fields.String()

    order = OrderComplex.from_dict(
        {
            'status': 'good',
            '_object_type': "OrderComplex"
        }, doc_id="1"
    )

    assert isinstance(order, OrderComplex)

    """
    TODO: assert that this code fails (currently does not fail)
    
        order = DomainModel.from_dict(
        {
            'status': 'good',
            '_object_type': "Order"
        }, doc_id="SF"
    )
    
    """

    assert order.to_dict() == {
        '_object_type': 'OrderComplex',
        'doc_id': '1',
        'doc_ref': 'OrderComplex/1',
        'status': 'good'}

    class Order(DomainModel):
        """
        Example of a use case of excluding "obj_type", "doc_id", and "doc_ref"
        """

        class _schema_cls(PrimaryObjectSchema):
            class Meta:
                exclude = ("obj_type", "doc_id", "doc_ref")

            status = fields.String()

    order = Order.from_dict(
        {
            'status': 'good',
        }, doc_id="2"
    )

    assert order.to_dict() == {'status': 'good'}
