import typing
from functools import partial

from flask_boiler.mapper import fields
from typing import Type, Callable

from flask_boiler.common import _NA
from flask_boiler.query.cmp import Condition, RootCondition

_ATTRIBUTE_STORE_NAME = "_attrs"

class ValueNotProvided:
    pass


class AttributeBase(RootCondition):

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        field_cls: Type[fields.Field] = fields.Field
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __set_name__(self, owner, name):
        self.parent = owner
        self.name = name

    def copy(self):
        """
        TODO: debug
        NOTE: contents in self.field_kwargs may or may not be copied
        TODO: fix
        :return:
        """
        from copy import deepcopy
        return deepcopy(self)

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
            *,
            initialize:bool= _NA,
            initializer: typing.Union[Callable[[object], None], _NA] = _NA,
            data_key=_NA,

            import_enabled:bool= _NA,
            import_default=_NA,
            import_required=_NA,

            export_enabled:bool= _NA,
            export_default=_NA,
            export_required=_NA,

            requires=_NA,

            type_cls=_NA,

    ):
        """

        :param initialize: If true, initialize the value as the first step.
            The value may be set again later in the process of calling "new".
        :param initialize_value: The value to initialize the attribute to.
            May be a callable to avoid mutable default arguments.

        :param data_key: Sets import_from and export_to (field name in a
            document in the database)

        :param import_enabled: If true, the value will be imported
            to the object; Default to True.
        :param import_default: Import this value if the field
            name is missing from a document in the database
        :param import_required:

        :param export_enabled: If true, the value will be exported to
            a field in the database. Default to True.
        :param export_default: Export this value if attribute
            is missing from the object

        :param requires: A list of attributes that is required to be
            imported before this attribute is imported (do not pass
            in values that may result in a cycle, or you risk infinite
            call loop)  TODO: implement circular dependency detection

        :param type_cls: type for the attribute (no use for now)
        """
        super().__init__()
        field_kwargs = dict()

        field_kwargs["allow_none"] = True

        """
        Initialization precedes import 
        """


        if initialize is _NA:
            initialize = False

        self.initialize = initialize

        """
        Initializer: used to initialize the attribute when 
            attr.initialize is set to True. 
        """
        if initializer is _NA:
            def _initializer_not_defined(_self):
                raise NotImplementedError
            initializer = _initializer_not_defined

        self.initializer = initializer

        # Parse data key
        if data_key != _NA:
            field_kwargs["data_key"] = data_key

        """
        Code for import (deserialization)
        """

        if import_enabled == _NA:
            self.import_enabled = True
        else:
            self.import_enabled = import_enabled

        if self.import_enabled:
            # Default value when key is not found during import
            if import_default == _NA:
                self.import_default = fields.allow_missing
            else:
                self.import_default = import_default
            field_kwargs["missing"] = self.import_default

            # whether to raise error when key is not found during import
            if import_required == _NA:
                self.import_required = False
            else:
                self.import_required = import_required
            field_kwargs["required"] = self.import_required
        else:
            field_kwargs["dump_only"] = True

        """
        Code for export (Serialization)
        """
        if export_enabled == _NA:
            self.export_enabled = True
        else:
            self.export_enabled = export_enabled

        if self.export_enabled:
            # Default value when attribute is not found during export
            if export_default == _NA:
                self.export_default = fields.allow_missing
            else:
                self.export_default = export_default
            field_kwargs["missing"] = self.export_default

            # whether to raise error when key is not found during export
            if export_required == _NA:
                self.export_required = False
            else:
                self.export_required = export_required
        else:
            # TODO: test code behaviors when both load_only and
            #   dump_only are true
            field_kwargs["load_only"] = True

        # To be used by self._make_field
        self._field_kwargs = field_kwargs

        """
        To be set by __set_name__ when attribute instance is binded
            to a class
        """
        self.parent = _NA
        self.name = _NA

        if requires == _NA:
            requires = list()
        else:
            raise NotImplementedError
        self.requires = requires
        self.type_cls = type_cls


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

    TODO: note that later definition of a getter/setter may override earlier
    TODO:   definitions. (this may happen when you subclass a class)

    TODO: check for memory leak
    """

    def  __init__(self,
                  *, fget=None, fset=None, fdel=None, doc=None,
                  **kwargs):

        """
        Getter
        """

        self.fget = fget

        """
        Setter
        """

        self.fset = fset

        """
        Deleter 
        """

        self.fdel = fdel

        self.__doc__ = doc
        """
        TODO: check that __doc__ is forwarded 
        """

        super().__init__(**kwargs)

    # @typing.overload
    # def __get__(self, instance: typing.Any, owner: typing.Any):
    #     ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            fget = self.fget
            if fget is None:
                def fget(_self):
                    inner = getattr(_self, _ATTRIBUTE_STORE_NAME)
                    return getattr(inner, self.name)
            return fget(instance)

    def __set__(self, instance, value):
        if instance is None:
            raise ValueError
        else:
            fset = self.fset
            if fset is None:
                def fset(_self_obj, value):
                    inner = getattr(_self_obj, _ATTRIBUTE_STORE_NAME)
                    return setattr(inner, self.name, value)
            fset(instance, value)

    def __delete__(self, instance):
        if instance is None:
            raise ValueError
        else:
            fdel = self.fdel
            if fdel is None:
                def fdel(_self):
                    inner = getattr(_self, _ATTRIBUTE_STORE_NAME)
                    return delattr(inner, self.name)
            fdel(instance)

    def getter(self, fget):
        _self = self.copy()
        _self.fget = fget
        return _self

    def setter(self, fset):
        _self = self.copy()
        _self.fset = fset
        return _self

    def deleter(self, fdel):
        _self = self.copy()
        _self.fdel = fdel
        return _self

    def init(self, initializer):
        _self = self.copy()
        _self.initializer = initializer
        return _self


class DictAttribute(PropertyAttribute):

    def __init__(self, **kwargs):

        def _dict_initializer(_self):
            attr_name = self.name
            setattr(_self, attr_name, dict())

        super().__init__(
            initialize=True,
            initializer=_dict_initializer,
            **kwargs)


class RelationshipAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        field_cls = fields.Relationship
        one = field_cls(**self._field_kwargs, attribute=self.name)

        if self.collection is None:
            return one
        elif self.collection is dict:
            # TODO: test rigorously; see if the name _Temporary__make_field may
            #     cause it to be affected by another run of _make_field
            dict_field_cls = type(
                '_Temporary__make_field',
                (fields.Mapping,),
                {
                    'mapping_type': self.collection
                })
            return dict_field_cls(values=one)
        elif self.collection is list:
            # TODO: confirm that set and tuple and etc. are compatible
            list_field_cls = fields.List
            return list_field_cls(one)
        else:
            raise NotImplementedError

    def __init__(self, *, nested=_NA, collection=_NA, dm_cls=_NA, **kwargs):
        # TODO: compare _NA everywhere with "is" rather than "=="
        super().__init__(
            **kwargs
        )
        if nested == _NA:
            raise ValueError
        else:
            self.nested = nested
        if self.nested:
            self._field_kwargs["nested"] = self.nested

        if collection == _NA:
            collection = None
        self.collection = collection

        if dm_cls == _NA:
            dm_cls = None
        self.dm_cls = dm_cls
        self._field_kwargs["obj_type"] = self.dm_cls


class LocalTimeAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        field_cls = fields.Localtime
        return field_cls(**self._field_kwargs, attribute=self.name)


class DocRefAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        field_cls = fields.DocRefField
        return field_cls(**self._field_kwargs, attribute=self.name)


class ReferenceAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        field_cls = fields.StructuralRef
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, many=_NA, dm_cls=_NA, missing=_NA, **kwargs):
        super().__init__(
            **kwargs
        )

        if many == _NA:
            many = False
        self.many = many
        self._field_kwargs["many"] = self.many

        if missing == _NA:
            missing = None
        self.missing = missing
        self._field_kwargs['missing'] = missing

        if dm_cls == _NA:
            dm_cls = None
        self.dm_cls = dm_cls
        self._field_kwargs["obj_type"] = self.dm_cls


class EmbeddedAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        field_cls = fields.Embedded
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, many=_NA, obj_cls=_NA, **kwargs):
        super().__init__(
            **kwargs
        )

        if many == _NA:
            many = False
        self.many = many
        self._field_kwargs["many"] = self.many

        if obj_cls == _NA:
            obj_cls = None
        self.dm_cls = obj_cls
        self._field_kwargs["obj_type"] = self.dm_cls


class ObjectTypeAttribute(PropertyAttribute):

    def _make_field(self) -> fields.Field:
        field_cls = fields.ObjectTypeField
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, f_serialize=_NA, f_deserialize=_NA, **kwargs):
        super().__init__(
            **kwargs
        )
        self._field_kwargs["serialize"] = f_serialize
        self._field_kwargs["deserialize"] = f_deserialize


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
