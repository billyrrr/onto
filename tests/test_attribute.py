import pytest
from flask_boiler.attributes import attribute
from flask_boiler.attributes.attribute import PropertyAttribute, \
    ForwardInnerAttribute, Attribute, AttributeBase
from flask_boiler import models
from flask_boiler.model_registry import ModelRegistry, BaseRegisteredModel

import typing

def test_binding():
    class A(object):
        i = attribute.AttributeBase()

    assert isinstance(A.i, attribute.AttributeBase)

    with pytest.raises(AttributeError):
        _ = A().i


class A(object):

    i = PropertyAttribute()

    @i.getter
    def i(self) -> int:
        return self._i

    @i.setter
    def i(self, value):
        self._i = value


def test_property():
    a = A()
    a.i = 1
    assert a.i == 1
    assert isinstance(a.i, int)
    assert isinstance(A.i, PropertyAttribute)


class B(object):

    i: int = ForwardInnerAttribute(inner_name="aa")


def test_forward_inner():

    b = B()
    a = A()
    a.i = 1
    b.aa = a
    assert b.i == a.i == 1


class C(models.ModelBase):

    i = PropertyAttribute()


def test_property_attribute():

    c = C()
    c.i = 2
    assert c.i == 2
