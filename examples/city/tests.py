import pytest
from google.cloud.firestore_v1 import DocumentSnapshot

from onto.context import Context as CTX
from onto.testing_utils import _wait
from tests.utils import _delete_all

from .views import CityView
from .models import Municipality


@pytest.fixture
def tok_snapshot(request) -> DocumentSnapshot:
    obj = Municipality.new(
        doc_id="TOK", city_name='Tokyo', country='Japan', capital=True)
    obj.save()

    def fin():
        _delete_all(collection_name="City", CTX=CTX)
        _delete_all(collection_name="cityView", CTX=CTX)

    request.addfinalizer(fin)

    return CTX.db.document(obj.doc_ref_str).get()


def test_new_with_snapshot(tok_snapshot):
    view = CityView.new(snapshot=tok_snapshot)


def test_view_mediator(tok_snapshot):
    from .main import city_view_mediator
    city_view_mediator.start()
    _wait()
    res = CTX.db.document("cityView/TOK").get().to_dict()
    assert res == {
        'doc_ref': 'cityView/TOK',
        'obj_type': 'CityView',
        'country': 'Japan',
        'name': 'Tokyo'
    }


@pytest.fixture
def user_form(request):
    doc_ref = CTX.db.document("users/uid1/cityForms/LA")

    def fin():
        _delete_all(subcollection_name="cityForms", CTX=CTX)
        _delete_all(collection_name="City", CTX=CTX)

    request.addfinalizer(fin)

    doc_ref.create(
        dict(
            name='Los Angeles',
            country='USA'
        )
    )


def test_form_mediator(user_form):

    from .main import city_form_mediator
    city_form_mediator.start()
    _wait()
    res = CTX.db.document("City/LA").get().to_dict()

    assert res == {
        'cityName': 'Los Angeles',
        'country': 'USA',
        'doc_id': 'LA',
        'doc_ref': 'City/LA',
        'obj_type': 'City'
    }

    from .main import city_view_mediator
    city_view_mediator.start()
    _wait()
    res = CTX.db.document("cityView/LA").get().to_dict()
    assert res == {
        'name': 'Los Angeles',
        'country': 'USA',
        'doc_ref': 'cityView/LA',
        'obj_type': 'CityView',
    }


"""
Recipe for metaclass __prepare__ 
Plan to use this recipe to pull Attribute objects declared in superclass 
to local namespace to be used directly in class declaration. 

"""

# def test_exp():
#     class Meta(type):
#     def __prepare__(name, bases, **kwds):
#         print("preparing {}".format(name), kwds)
#         my_list = []
#         for b in bases:
#             if hasattr(b, 'my_list'):
#                 my_list.extend(b.my_list)
#         return {'my_list': my_list}
#
# class A(metaclass=Meta):
#     my_list = ["a"]
#
# class B(A):
#     my_list.append(2)
#
# print(A().my_list)
# print(B().my_list)
