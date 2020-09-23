from unittest import mock

import pytest
from onto.attrs import attribute
from onto.attrs.attribute import PropertyAttribute, \
    ForwardInnerAttribute, Attribute, AttributeBase

from onto.models.base import Serializable


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


class C(Serializable):

    class Meta:
        pass

    i = PropertyAttribute()


def test_property_attribute():

    c = C()
    c.i = 2
    assert c.i == 2





def test_initializer():

    f = mock.Mock(return_value=None, __name__='i')

    class D(Serializable):
        class Meta:
            pass

        i = PropertyAttribute(initialize=True)
        # i = PropertyAttribute()

        # i = i.init(f)

        @i.init
        def i(self):
            f()

    d = D()
    d.i = 2
    assert d.i == 2
    f.assert_called_once()


class E(Serializable):

    class Meta:
        pass

    i = PropertyAttribute(initialize=False)

    i = i.init(mock.Mock(return_value=None, __name__='i'))


def test_initializer_not_called():

    e = E()
    e.i = 2
    assert e.i == 2
    E.i.initializer.assert_not_called()


def test_copy():

    a = E.i
    b = E.i.copy()
    assert a is not b


def test_import_only():

    class K(Serializable):
        class Meta:
            import_only = True

        i = PropertyAttribute(initialize=False)

        i = i.init(mock.Mock(return_value=None, __name__='i'))

    k = K.new(i=1)
    assert 'i' not in k.to_dict()
