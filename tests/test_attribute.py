import pytest
from flask_boiler.attributes import attribute


def test_binding():
    class A(object):
        i = attribute.AttributeBase()

    assert isinstance(A.i, attribute.AttributeBase)

    with pytest.raises(AttributeError):
        _ = A().i


class PropertyAttribute(attribute.AttributeBase):
    """
    Ref: https://blog.csdn.net/weixin_43265804/article/details/82863984
        content under CC 4.0
    """

    def __init__(self, *, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        super().__init__(**kwargs)
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.fget(instance)

    def __set__(self, instance, value):
        self.fset(instance, value)

    def __delete__(self, instance):
        self.fdel(instance)

    def getter(self, fget):
        self.fget = fget
        return self

    def setter(self, fset):
        self.fset = fset
        return self

    def deleter(self, fdel):
        self.fdel = fdel
        return self


class Attribute(attribute.AttributeBase):

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return getattr(instance._attribute_store, self.name)

    def __set__(self, instance, value):
        setattr(instance._attribute_store, self.name, value)

    def __delete__(self, instance):
        delattr(instance._attribute_store, self.name)



class ForwardInnerAttribute(PropertyAttribute):

    def __init__(self, *, inner_name, **kwargs):

        def fget(_self):
            inner = getattr(_self, inner_name)
            return getattr(inner, self.name)

        def fset(_self, value):
            inner = getattr(_self, inner_name)
            return setattr(inner, self.name, value)

        super().__init__(fget=fget, fset=fset, **kwargs)


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

    i = ForwardInnerAttribute(inner_name="aa")


def test_forward_inner():

    b = B()
    a = A()
    a.i = 1
    b.aa = a
    assert b.i == a.i == 1
