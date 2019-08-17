from src import fields
from src.schema import Schema
from src.domain_model import DomainModel
from src.view_model import ViewModel


def test_bind_to():

    class TestViewObject(ViewModel):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    obj = TestViewObject.create("viewId1")

    class TestDomainSchema1(Schema):
        property_a = fields.Raw(load_from="propertyA", dump_to="propertyA")

    class TestDomainObject1(DomainModel):

        _schema_cls = TestDomainSchema1

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.property_a = "hello"

    class TestDomainSchema2(Schema):
        property_b = fields.Raw(load_from="propertyB", dump_to="propertyB")

    class TestDomainObject2(DomainModel):

        _schema_cls = TestDomainSchema2

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.property_b = "world"

    dependent_obj_1 = TestDomainObject1.create("dependentId1")
    ref_1: str = dependent_obj_1.doc_ref.path
    obj.bind_to(ref_1)

    dependent_obj_2 = TestDomainObject2.create("dependentId2")
    ref_2: str = dependent_obj_2.doc_ref.path
    obj.bind_to(ref_2)

    # TODO: implement


