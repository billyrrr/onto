from flask_boiler import fields
from flask_boiler.schema import Schema
from flask_boiler.domain_model import DomainModel
from flask_boiler.view_model import ViewModel
from flask_boiler.firestore_object import FirestoreObjectClsFactory

import pytest

from .fixtures import CTX


@pytest.mark.usefixtures("CTX")
def test_create(CTX):

    class EmptySchema(Schema):
        pass

    # TestViewObject = FirestoreObjectClsFactory.create(
    #     name="TestViewObject",
    #     schema=EmptySchema,
    #     base=ViewModel
    # )

    # obj = TestViewObject.create("viewId1")

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


