import typing

from flask_boiler import fields
from typing import Type, Generic, TypeVar, Optional

from flask_boiler.model_registry import ModelRegistry, BaseRegisteredModel


class ValueNotProvided:
    pass


class _NA:
    pass


class AttributeBase:

    field_cls: Type[fields.Field] = None

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        return fields.Field()

    def __set_name__(self, owner, name):
        self.parent = owner
        self.name = name

    def __get__(self, instance, owner):
        """ Only allow attribute object to be invoked "get" on
                a class, and not an instance.

        :param instance:
        :param owner:
        :return:
        """
        if instance is None:
            return self
        else:
            raise AttributeError()

    def __init__(
            self,
            # *,
            # initialize,
            # initialize_value,
            # data_key,
            #
            # import_enabled,
            # import_default,
            # import_required,
            #
            # export_enabled,
            # export_default,
            # export_required,
            #
            type_cls=None,

    ):
        """

        :param initialize: If true, initialize the value as the first step.
            The value may be set again later in the process of calling "new".
        :param initialize_value: The value to initialize the attribute to.
            May be a callable to avoid mutable default arguments.
        :param data_key: Sets import_from and export_to (field name in a
            document in the database)

        :param import_enabled: If true, the value will be imported
            to the object
        :param import_default: Import this value if the field
            name is missing from a document in the database
        :param import_required:

        :param export_enabled: If true, the value will be exported to
            a field in the database
        :param export_default: Export this value if attribute
            is missing from the object
        :param export_required:

        """
        # self._field = self.field_cls(
        #     # missing=value_if_not_loaded
        # )

        # To be set by __set_name__ when attribute instance is binded
        #   to a class
        self.parent = _NA
        self.name = _NA


class Boolean(AttributeBase):
    """Field that serializes to a boolean and deserializes
        to a boolean.
    """
    pass

    # def __init__(
    #         self,
    #         *,
    #         initialize,
    #         initialize_value,
    #         data_key,
    #
    #         import_enabled,
    #         import_default,
    #         import_required,
    #
    #         export_enabled,
    #         export_default,
    #         export_required,
    #
    #         type_cls: Optional[Type[T]],):
    #
    #     res = dict()
    #
    #     res["import_only"], res["export_only"] = \
    #         import_enabled and not export_enabled, \
    #         export_enabled and not import_enabled
    #
    #     if import_enabled:
    #         res["required"] = import_required
    #
    #     super().__init__(
    #
    #         value_if_not_loaded=value_if_not_loaded,
    #         nullable=True,
    #         *args,
    #         **kwargs
    #     )
    #
    # def __get__(self, instance, owner) -> bool:
    #     return super().__get__(instance, owner)


class PropertyAttribute(AttributeBase):
    """
    Ref: https://blog.csdn.net/weixin_43265804/article/details/82863984
        content under CC 4.0
    """

    def  __init__(self,
                 *, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        super().__init__(**kwargs)
        if fget is None:
            def fget(_self):
                inner = getattr(_self, "_attribute_store")
                return getattr(inner, self.name)
        self.fget = fget
        if fset is None:
            def fset(_self, value):
                inner = getattr(_self, "_attribute_store")
                return setattr(inner, self.name, value)
        self.fset = fset

        self.fdel = fdel
        self.__doc__ = doc

    # @typing.overload
    # def __get__(self, instance: typing.Any, owner: typing.Any):
    #     ...

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


class Attribute(AttributeBase):

    def __init__(
            self,
            *,
            type_cls=None,
            **kwargs,
    ):
        super().__init__(type_cls=type_cls, **kwargs)

    @typing.overload
    def __get__(self, instance, owner) -> int:
        pass

    def __get__(self, instance, owner) -> typing.Any:
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
