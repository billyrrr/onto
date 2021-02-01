import typing
from collections import namedtuple
from functools import partial, lru_cache

try:
    from pony.orm.core import Attribute, PrimaryKey, Discriminator, Optional, Required
except ImportError:
    import warnings
    warnings.warn("pony import skipped")

from onto.mapper import fields
from typing import Type, Callable

from onto.common import _NA
from onto.query.cmp import Condition, RootCondition

from functools import cached_property

_ATTRIBUTE_STORE_NAME = "_attrs"

class ValueNotProvided:
    pass


class TypeClsAsArgMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MakePonyAttribute:

    def _make_pony_attribute_cls(self):
        if self.__class__.__name__ == "Discriminator":
            # TODO: make better
            return Discriminator
        if self.import_required:
            return Required
        else:
            return Optional

    # @lru_cache(maxsize=None)
    def _make_pony_attribute(self):
        column_name = self.data_key
        py_type = self.type_cls
        is_required = self.import_required
        _pony_attribute_cls = self._make_pony_attribute_cls()
        _pony_attribute = _pony_attribute_cls(
            py_type, is_required=is_required, column=column_name)
        return _pony_attribute

    @cached_property
    def _pony_attribute(self):
        if self.is_concrete:
            return self._make_pony_attribute()
        else:
            return None

    @property
    def is_collection(self):
        return self._pony_attribute.is_collection


udf = namedtuple('udf', ['f', 'fid', 'd', 'result_pytype'])


class MakePonyFunction:

    assigned_ids = set()

    @classmethod
    def _random_func_id(cls, N=5):
        import random, string
        fid = '_onto_udf_' + ''.join(random.choices(string.ascii_lowercase, k=N))
        if fid in cls.assigned_ids:
            raise ValueError("Collision")
        cls.assigned_ids.add(fid)
        return fid

    @classmethod
    def register_function(cls, f, type_cls):
        class Some:
            pass

        # TODO: add notes about `typing.*` not supported

        # import ast
        # code = f.__code__
        import inspect
        d = list(inspect.getclosurevars(f).unbound)

        def k(*args):
            _self = Some()
            for idx in range(len(d)):
                k = d[idx]
                v = args[idx]
                setattr(_self, k, v)
            _f = f
            from types import MethodType
            _f = MethodType(f, _self)
            return _f()

        fid = cls._random_func_id()
        udf_obj = udf(f=k, fid=fid, d=d, result_pytype=type_cls)
        # f_reg.append(udf_obj)
        return udf_obj

    @staticmethod
    def _flink_type_mapping(type_cls):
        from pyflink.table.types import _type_mappings
        return _type_mappings[type_cls]

    @classmethod
    def _register_flink_function(cls, udf_obj: udf):
        from pyflink.table import ScalarFunction, DataTypes
        from pyflink.table import udf as flink_udf
        F = type(udf_obj.fid, bases=(ScalarFunction,), dict={
            'eval': udf_obj.f,
        })
        table_env.create_temporary_function(
            udf_obj.fid,
            flink_udf(
                F(),
                input_types=[cls._flink_type_mapping(v) for _, v in udf_obj.d.items()],  # TODO: ensure order of keys
                result_type=cls._flink_type_mapping(udf_obj.result_pytype)
            )
        )
        # flink_udf()

#
# @db.on_connect(provider='flink')
# def _add_udf(db, connection):
#     # cursor = connection.cursor()
#
#     def create_function(name, num_params, func):
#         from pony.orm.dbproviders.sqlite import keep_exception
#         func = keep_exception(func)
#         connection.create_function(name, num_params, func)
#
#     for udf in f_reg:
#         create_function(udf.fid, len(udf.d), udf.f)


class AttributeBase(RootCondition):

    def __hash__(self):
        # TODO: debug
        return id(self)

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.Field

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        field_cls = self._make_field_cls()
        return field_cls(**self._field_kwargs, attribute=self.name)

    def _get_data_key(self):
        """
        TODO: deprecate
        :return:
        """
        return self.data_key

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

    def _get_select(self, instance):
        return getattr(instance, self.name)

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

    @property
    def data_key(self):
        if self._data_key is not None:
            return self._data_key
        else:
            return self.name

    @property
    def is_internal(self):
        return not self.import_enabled and not self.export_enabled

    @property
    def pytype(self):
        return self.type_cls

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
            doc=_NA,
            is_concrete=_NA,
            validate=_NA,
            **kwargs

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
        :param validate: validate arg to pass to marshmallow
        """
        super().__init__(**kwargs)
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
            self._data_key = data_key
            field_kwargs["data_key"] = data_key
        else:
            self._data_key = None

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

        if doc == _NA:
            doc = None
        self.doc = doc

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

        if is_concrete is _NA:
            is_concrete = False
        self.is_concrete = is_concrete

        if validate is not _NA:
            self._field_kwargs['validate'] = validate


class Boolean(AttributeBase, MakePonyAttribute):

    # def _make_graphql_type(self):
    #     import graphql
    #     return graphql.GraphQLBoolean


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


class PropertyAttributeBase(AttributeBase):
    """
    Ref: https://blog.csdn.net/weixin_43265804/article/details/82863984
        content under CC 4.0

    TODO: note that later definition of a getter/setter may override earlier
    TODO:   definitions. (this may happen when you subclass a class)

    TODO: check for memory leak
    """

    def  __init__(self,
                  *, fget=None, fset=None, fdel=None,
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

        """
        TODO: check that __doc__ is forwarded 
        """

        super().__init__(**kwargs)

    # @typing.overload
    # def __get__(self, instance: typing.Any, owner: typing.Any):
    #     ...

    def _get_select(self, instance):
        return self.fget()

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
        # fget = _self._register_pony_function(fget)
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


class PropertyAttribute(PropertyAttributeBase, MakePonyAttribute):
    pass


class DictAttribute(PropertyAttribute):

    # def _make_field(self) -> fields.Field:
    #     """
    #     TODO: implement
    #     :return:
    #     """
    #     field_cls: Type[fields.Field] = fields.Dict
    #     return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, **kwargs):

        def _dict_initializer(_self):
            attr_name = self.name
            setattr(_self, attr_name, dict())

        super().__init__(
            initialize=True,
            initializer=_dict_initializer,
            **kwargs)


class RelationshipAttribute(PropertyAttributeBase, MakePonyAttribute):

    def _make_pony_attribute_cls(self):
        from pony.orm.core import Set
        collection_type = self.collection
        if collection_type is not None:
            return Set
        else:
            return super()._make_pony_attribute_cls()

    # @lru_cache(maxsize=None)
    def _make_pony_attribute(self):
        # column_name = self.data_key
        # TODO: Column name has no actual use; so it is not allowed in pony
        py_type = self.dm_cls
        is_required = self.import_required
        reverse = self.reverse if isinstance(self.reverse, str) or self.reverse is None else self.reverse.data_key
        _pony_attribute_cls = self._make_pony_attribute_cls()
        d = dict(is_required=is_required, reverse=reverse)
        if self.data_key != self.name:  # TODO: make better
            d['column'] = self.data_key
        _pony_attribute = _pony_attribute_cls(py_type, **d)
        return _pony_attribute

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.Relationship

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        field_cls = self._make_field_cls()
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

    def __init__(self, *, nested=_NA, collection=_NA, dm_cls=_NA, reverse=_NA, **kwargs):
        # TODO: compare _NA everywhere with "is" rather than "=="
        super().__init__(
            **kwargs,
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

        if reverse is _NA:
            reverse = None
        self.reverse = reverse

    @property
    def pytype(self):
        if self.collection is None:
            return self.dm_cls
        else:
            raise TypeError  # TODO: make better


class LocalTimeAttribute(PropertyAttribute):

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.Localtime

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
        return field_cls(**self._field_kwargs, attribute=self.name)


class StringAttribute(PropertyAttribute):
    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.String


class DocRefAttribute(PropertyAttributeBase, MakePonyAttribute):

    def _make_pony_attribute_cls(self):
        return PrimaryKey

    # @lru_cache(maxsize=1)
    def _make_pony_attribute(self):
        column_name = self.data_key
        py_type = self.type_cls
        _pony_attribute_cls = self._make_pony_attribute_cls()
        _pony_attribute = _pony_attribute_cls(
            py_type, column=column_name)
        return _pony_attribute

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.DocRefField

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
        return field_cls(**self._field_kwargs, attribute=self.name)


class MultiDocRefAttribute(AttributeBase, MakePonyAttribute):

    def _make_pony_attribute_cls(self):
        return PrimaryKey

    def __init__(self, *attrs):
        self.attributes = list(attrs)
        self.is_concrete = True

    # @lru_cache(maxsize=1)
    def _make_pony_attribute(self):
        _pony_attribute_cls = self._make_pony_attribute_cls()
        _pony_attribute = _pony_attribute_cls(*(attr._pony_attribute for attr in self.attributes))
        return _pony_attribute


    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.DocRefField

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
        return field_cls(attribute=self.name)


class ReferenceAttribute(PropertyAttribute):

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.StructuralRef

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
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

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.Embedded

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, type_cls=_NA, collection=_NA, **kwargs):

        super().__init__(
            type_cls = type_cls,
            **kwargs
        )

        # if many == _NA:
        #     many = False
        # self.many = many
        # self._field_kwargs["many"] = self.many

        if type_cls == _NA:
            type_cls = None

        # self.type_cls = obj_cls
        # self._field_kwargs["obj_type"] = self.dm_cls

        if collection == _NA:
            collection = None
        else:
            self._field_kwargs["many"] = True
        self.collection = collection




class ObjectTypeAttribute(PropertyAttributeBase, TypeClsAsArgMixin):

    def _make_field_cls(self):
        # Makes marshmallow field cls
        return fields.ObjectTypeField

    def _make_field(self) -> fields.Field:
        field_cls = self._make_field_cls()
        return field_cls(**self._field_kwargs, attribute=self.name)

    def __init__(self, f_serialize=_NA, f_deserialize=_NA, **kwargs):
        super().__init__(
            **kwargs,
            # TODO: recover
            # column=self.data_key
        )
        self._field_kwargs["serialize"] = f_serialize
        self._field_kwargs["deserialize"] = f_deserialize

#
# class Attribute(AttributeBase):  # TODO: change
#
#     def __init__(
#             self,
#             *,
#             type_cls=None,
#             **kwargs,
#     ):
#         super().__init__(type_cls=type_cls, **kwargs)
#
#     @typing.overload
#     def __get__(self, instance, owner) -> int:
#         pass
#
#     def __get__(self, instance, owner) -> typing.Any:
#         if instance is None:
#             return self
#         else:
#             return getattr(instance._attribute_store, self.name)
#
#     def __set__(self, instance, value):
#         setattr(instance._attribute_store, self.name, value)
#
#     def __delete__(self, instance):
#         delattr(instance._attribute_store, self.name)


class ForwardInnerAttribute(PropertyAttribute):

    def __init__(self, *, inner_name, **kwargs):

        def fget(_self):
            inner = getattr(_self, inner_name)
            return getattr(inner, self.name)

        def fset(_self, value):
            inner = getattr(_self, inner_name)
            return setattr(inner, self.name, value)

        super().__init__(fget=fget, fset=fset, **kwargs)
