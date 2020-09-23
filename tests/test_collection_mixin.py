import pytest

from onto import collection_mixin, domain_model
from abc import ABC
from .fixtures import CTX


def test_init():

    class ExampleMixin(collection_mixin.CollectionMixin):
        _collection_name = "Examples"

    assert ExampleMixin._collection_name == "Examples"


@pytest.fixture
def ExampleMixin(CTX):

    class ExampleMixin(collection_mixin.CollectionMixin):
        _collection_name = "Examples"

        @classmethod
        def _datastore(cls):
            return CTX.dbs.firestore

    return ExampleMixin


def test_get_collection(CTX, ExampleMixin):
    assert ExampleMixin._get_collection().id == "Examples"


def test_get_collection_name(CTX, ExampleMixin):
    assert ExampleMixin._get_collection_name() == "Examples"


def test_mixin_instance_methods(CTX, ExampleMixin):
    example = ExampleMixin()
    assert example.collection_name == "Examples"
    assert example.collection.id == "Examples"


def test_mix_metaclass(CTX):

    class ExampleMetaclassObject(ABC):

        example_static_attr = "example_static_attr"

        def example_method(self):
            return "example_method"

        @classmethod
        def example_cls_method(cls):
            return "example_cls_method"

    class ExampleMixedClass(ExampleMetaclassObject,
                            collection_mixin.CollectionMixin,
                            ):
        _collection_name = "Examples"

    assert ExampleMixedClass._collection_name == "Examples"

    assert ExampleMixedClass.example_static_attr == "example_static_attr"
    assert ExampleMixedClass.example_cls_method() == "example_cls_method"

    example = ExampleMixedClass()
    assert example.example_method() == "example_method"

