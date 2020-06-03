import pytest
from google.cloud.firestore_v1 import DocumentSnapshot, DocumentReference

from flask_boiler.view.query_delta import make_snapshot
from .fixtures import CTX
from .test_domain_model import setup_cities, City

from flask_boiler.query.cmp import v


@pytest.mark.usefixtures("setup_cities")
def test_query_with_attr_str():

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

    for obj in City.where(country=("==", "USA")):
        d = obj.to_dict()
        res_dict[d["cityName"]] = d

    assert res_dict['Washington D.C.'] == expected_dict['Washington D.C.']
    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


@pytest.mark.usefixtures("setup_cities")
def test_query_with_cmp():

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

    for obj in City.where(v.country == "USA", v.city_state == "CA"):
        d = obj.to_dict()
        res_dict[d["cityName"]] = d

    assert res_dict['San Francisco'] == expected_dict['San Francisco']
    assert res_dict['Los Angeles'] == expected_dict['Los Angeles']


def test_trigger_snapshot(CTX):
    data = {"oldValue": {}, "updateMask": {},
            "value": {"createTime": "2020-06-03T00:23:18.348623Z",
                      "fields": {"a": {"stringValue": "b"}},
                      "name": "projects/flask-boiler-testing/databases/(default)/documents/gcfTest/36ea7LTtYJHpW4yJQCp2",
                      "updateTime": "2020-06-03T00:23:18.348623Z"}}

    snapshot = make_snapshot(data['value'], client=CTX.db)
    assert isinstance(snapshot, DocumentSnapshot)
    assert snapshot.to_dict() == {'a': 'b'}
    assert snapshot.create_time is not None
    assert snapshot.update_time is not None

    assert make_snapshot(dict(), client=CTX.db) is None
