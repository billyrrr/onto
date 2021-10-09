import enum
import typing
from collections import namedtuple
from functools import partial, lru_cache

from onto.attrs.unit import Monad, MonadPrependMixin

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


class AttributeMixin(RootCondition, Monad, MonadPrependMixin):

    def __hash__(self):
        # TODO: debug
        return id(self)

    def _make_field(self) -> fields.Field:
        """
        TODO: implement
        :return:
        """
        raise NotImplementedError
        # return self.marshmallow_field
        # field_cls = self._make_field_cls()
        # return field_cls(**self._field_kwargs, attribute=self.name)

    def _get_data_key(self):
        """
        TODO: deprecate
        :return:
        """
        return self.data_key

    # def __set_name__(self, owner, name):
    #     self.parent = owner
    #     self.name = name

    @property
    def name(self):
        return self.properties.name

    @property
    def parent(self):
        return self.properties.parent

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
        return getattr(instance, self.properties.name)

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


class PropertyMixin:
    """
    Ref: https://blog.csdn.net/weixin_43265804/article/details/82863984
        content under CC 4.0

    """

    # @typing.overload
    # def __get__(self, instance: typing.Any, owner: typing.Any):
    #     ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            fget = getattr(self.properties, 'fget')
            return fget(instance)

    def __set__(self, instance, value):
        if instance is None:
            raise ValueError
        else:
            fset = getattr(self.properties, 'fset')
            fset(instance, value)

    def __delete__(self, instance):
        if instance is None:
            raise ValueError
        else:
            fdel = getattr(self.properties, 'fdel')
            fdel(instance)


class AttributeBase(PropertyMixin, AttributeMixin):

    @property
    def marshmallow_field(self):
        try:
            return self.properties._marshmallow_field_constructor(self.properties)
        except Exception as e:
            raise ValueError(f'Failed creating marshmallow_field ') from e

    def _graphql_field_constructor(self):
        arguments = dict(self.properties._graphql_field_kwargs)
        # args = [arguments['type_']]
        # del arguments['type_']
        import graphql
        if not self.properties.is_input:
            from functools import partial
            field_base = graphql.GraphQLField

            def resolve_info(obj, context):
                value = getattr(obj, self.properties.name, None)
                if isinstance(value, enum.Enum):
                    value = value.value
                return value

            # def resolver(attributed, resolve_info):
            #     return attributed.graphql_field_resolve(resolve_info)
                # raise ValueError
            from onto.helpers.graphql import default_field_resolver

            field_base = partial(
                field_base,
                resolve=resolve_info)
        else:
            field_base = graphql.GraphQLInputField
        field = field_base(
            # *args,
            **arguments
        )
        return field

    @property
    def graphql_field(self):
        try:
            return self._graphql_field_constructor()
        except Exception as e:
            raise ValueError(f'Failed creating graphql for {self.name}') from e

    @property
    def annotation(self):
        if hasattr(self, 'parent'):
            owner = self.parent
            name = self.name
            annotations = typing.get_type_hints(owner)
            # annotations = getattr(owner, '__annotations__', None)
            if annotations is not None:
                if name in annotations:
                    return annotations[name]
