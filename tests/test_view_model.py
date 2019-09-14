import time

from google.cloud.firestore import DocumentReference

from examples.luggage_models import LuggageItem, Luggages
from flask_boiler import fields
from flask_boiler.schema import Schema
from flask_boiler.domain_model import DomainModel
from flask_boiler.view_model import ViewModel
from flask_boiler.collection_mixin import CollectionMixin
from flask_boiler.firestore_object import FirestoreObjectClsFactory

import pytest

from .fixtures import CTX


@pytest.mark.usefixtures("CTX")
def test_create(CTX):

    class EmptySchema(Schema):
        pass

    class DomainObjectBase(DomainModel):
        _collection_name = "tst_domain_objs"

    class DomainSchema1(Schema):
        property_a = fields.Raw(load_from="propertyA", dump_to="propertyA")

    DomainObject1 = FirestoreObjectClsFactory.create(
        name="DomainObject1",
        schema=DomainSchema1,
        base=DomainObjectBase
    )

    class DomainSchema2(Schema):
        property_b = fields.Raw(load_from="propertyB", dump_to="propertyB")

    DomainObject2 = FirestoreObjectClsFactory.create(
        name="DomainObject2",
        schema=DomainSchema2,
        base=DomainObjectBase
    )

    dependent_obj_1 = DomainObject1.create("dependentId1")
    ref_1_str: str = dependent_obj_1.doc_ref.path
    assert ref_1_str == "tst_domain_objs/dependentId1"

    dependent_obj_2 = DomainObject2.create("dependentId2")
    ref_2_str: str = dependent_obj_2.doc_ref.path
    assert ref_2_str == "tst_domain_objs/dependentId2"

    # TODO: implement

    ViewObject = FirestoreObjectClsFactory.create(
        name="TestViewObject",
        schema=EmptySchema,
        base_tuple=(ViewModel, )
    )

    # obj = TestViewObject.create("viewId1")


def test_binding(CTX):
    d_a = {
        "luggage_type": "large",
        "weight_in_lbs": 20,
        "obj_type": "LuggageItem"
    }
    id_a = "luggage_id_a"
    obj_a = LuggageItem.create(id_a)
    obj_a._import_properties(d_a)
    obj_a.save()

    d_b = {
        "luggage_type": "medium",
        "weight_in_lbs": 15,
        "obj_type": "LuggageItem"
    }
    id_b = "luggage_id_b"
    obj_b = LuggageItem.create(id_b)
    obj_b._import_properties(d_b)
    obj_b.save()

    vm_ref: DocumentReference = CTX.db.document(
        "test_lugagges/user_a_luggages")

    vm: Luggages = Luggages.create(vm_ref)

    vm.bind_to(key=id_a, obj_type="LuggageItem", doc_id=id_a)
    vm.bind_to(key=id_b, obj_type="LuggageItem", doc_id=id_b)

    # Takes time to propagate changes
    time.sleep(2)

    assert vm.to_dict() == {
        "luggages": [
            {
                "luggage_type": "large",
                "weight_in_lbs": 20
            },
            {
                "luggage_type": "medium",
                "weight_in_lbs": 15
            }
        ],
        "total_weight": 35,
        "total_count": 2,
        # "obj_type": "Luggages"
    }

    # Change the weight on one of the luggages
    obj_b.weight_in_lbs = 25
    obj_b.save()

    # Note that the update is eventually consistent with delays
    #   and local copies of a ViewModel should not be used to read
    #   updated values

    time.sleep(2)

    # # Test that the view model now has updated values
    assert vm.to_dict() == {
        "luggages": [
            {
                "luggage_type": "large",
                "weight_in_lbs": 20
            },
            {
                "luggage_type": "medium",
                "weight_in_lbs": 25
            }
        ],
        "total_weight": 45,
        "total_count": 2
    }
