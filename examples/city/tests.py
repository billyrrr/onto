import pytest
from google.cloud.firestore_v1 import DocumentSnapshot

from flask_boiler.context import Context as CTX
from flask_boiler.testing_utils import _wait
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
