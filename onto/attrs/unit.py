import contextlib


# Attribute
# - Serialization/Deserialization instructions
# - Validation
# - Precondition
# - Type
from collections import defaultdict

import typing
from functools import cached_property

from onto.common import _NA

class _ModelRegistry(type):
    """

    TODO: add exception handling when resolving classes
            that are destructed.

    Attributes:
    ===================
    _REGISTRY: dict
        key: name of the class
        value: class

    """

    _REGISTRY = {}
    _tree = defaultdict(set)
    _tree_r = defaultdict(set)

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        if new_cls.__name__ in mcs._REGISTRY:
            raise ValueError(
                "Class with name {} is declared more than once. "
                .format(new_cls.__name__)
            )
        mcs._REGISTRY[new_cls.__name__] = new_cls

        for base in bases:
            if issubclass(type(base), mcs):
                mcs._tree[base.__name__].add(new_cls.__name__)
                mcs._tree_r[new_cls.__name__].add(base.__name__)

        return new_cls

    @classmethod
    def get_registry(mcs):
        return dict(mcs._REGISTRY)

    @classmethod
    def _get_children_str(mcs, cls_name):
        return mcs._tree[cls_name].copy()

    @classmethod
    def _get_parents_str(mcs, cls_name):
        return mcs._tree_r[cls_name].copy()

    @classmethod
    def get_cls_from_name(mcs, obj_type_str):
        """ Returns cls from obj_type (classname string)
        obj_type must be a subclass of cls in current class/object
        """
        if obj_type_str in mcs._REGISTRY:
            return mcs._REGISTRY[obj_type_str]
        else:
            return None


class MonadPrependMixin:

    def __enter__(self):
        return self.as_root()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Monad:

    def __init__(self, decor):
        self.decor: DecoratorBase = decor

    @classmethod
    def _get_root(cls):
        return cls(decor=BranchHead())

    # def __mul__(cls, cls_b):
    #     import types
        # cls_r = types.new_class(
        #     name=cls.__name__ + cls_b.__name__,
        #     bases=(cls, cls_b),
        # )
        # return cls_r

    @property
    def properties(self):
        if isinstance(self, BranchHead):
            raise TypeError('use attrs.nothing to prevent duplicate attrs values')
        return self.decor

    @property
    def fget(self):
        return self.properties.make_fget(name=self.name)

    @property
    def fset(self):
        return self.properties.make_fset(name=self.name)

    @property
    def fdel(self):
        return self.properties.make_fdel(name=self.name)

    @staticmethod
    def get_decorator_cls(item):
        from onto.utils import camelize
        name = camelize(item, uppercase_first_letter=True)
        decorator_cls = _ModelRegistry.get_cls_from_name(obj_type_str=name)
        if decorator_cls is None:
            raise AttributeError(f'Unable to locate {name} in subclass of DecoratorBase (for decorator: {item})')
        return decorator_cls

    def __getattr__(self, item):
        decorator_cls = self.get_decorator_cls(item=item)
        decor = self.decor
        self_cls = self.__class__

        def output_wrapper(decorated):
            return self_cls(decor=decorated)
        try:
            f = decorator_cls.easy(decor=decor, output_wrapper=output_wrapper)
        except AttributeError:
            raise AttributeError(f'Unable to transform attribute with {item}')

        return f

    def descendant_of(self, cs):
        cs = set(self.get_decorator_cls(item=it) for it in cs)
        return self.properties.descendant_of(ancestors=cs)


class MonadContext(Monad, contextlib.ContextDecorator):

    stack = list()

    @classmethod
    def context(cls):
        return cls(decor=root_decor.get())

    def __enter__(self):
        self.stack.append( root_decor.set(self.decor) )

    def __exit__(self, exc_type, exc_val, exc_tb):
        root_decor.reset(self.stack.pop())
        return False
#
#
# class CurSelfContext(contextlib.ContextDecorator):
#
#     stack = list()
#
#     def __init__(self, cur_self):
#         self.cur_self = cur_self
#
#     def __enter__(self):
#         self.stack.append( cur_self.set(self.cur_self) )
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         cur_self.reset(self.stack.pop())
#         return False


class MarshmallowCapableBaseMixin:

    @staticmethod
    def _customize_field_cls(field_cls, methods):
        new_field_cls = type('tmp_field', (field_cls,), methods)
        return new_field_cls

        # if not method_name:
        #     method_name = unbound_method.__name__
        # bound_method = unbound_method.__get__(field_obj, field_obj.__class__)
        # setattr(field_obj, method_name, bound_method)

    @property
    def _marshmallow_field_constructor(self):
        def _constructor(_self):
            methods_overridden = dict(_self._marshmallow_field_override)
            field_cls = self._customize_field_cls(_self._marshmallow_field_cls, methods_overridden)
            field_obj = field_cls(
                **dict(_self._marshmallow_field_kwargs)
            )

            return field_obj
        return _constructor

    @property
    def _marshmallow_field_kwargs(self):
        yield from ()

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        return fields.Field

    @property
    def _marshmallow_field_override(self):
        yield from ()

class GraphqlCapableMixin:

    @property
    def _graphql_object_type(self):
        yield from ()

class DefaultDecoratorMixin(MarshmallowCapableBaseMixin, GraphqlCapableMixin):
    is_internal = False


import contextvars
root_decor = contextvars.ContextVar('root_decor', default=DefaultDecoratorMixin())
cur_self = contextvars.ContextVar('cur_self', default=None)

def whichever_order(li: list, operation):
    """
    Hack: try operation on all permutative orders of li until the one order does not trigger an error
    """
    n = len(li)
    from itertools import permutations
    errors = list()
    for t in permutations(li, n):
        try:
            new_list = list(t)
            return operation(new_list)
        except Exception as e:
            errors.append(e)
    else:
        raise Exception(f'All possible combinations failed {str(errors)}')

class DecoratorBase(metaclass=_ModelRegistry):
    """
    Can only create new state in self.
    Do not modify state of self.decorated

    """

    # @property
    # def origin(self):
    #     return cur_self.get()  # TODO: implement

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def easy_property(decorator_cls, decor, output_wrapper):
        decorated = decorator_cls.new(decorated=decor)
        return output_wrapper(decorated)

    @classmethod
    def easy_callable(decorator_cls, decor, output_wrapper):
        """
        Gets either a property or the initializer of a class
        """

        def f(*args, **kwargs):
            decorated = decorator_cls.new(*args, decorated=decor, **kwargs)
            return output_wrapper(decorated)

        return f

    @classmethod
    def easy(cls, *args, **kwargs):
        # Implemented verbosely by purpose to show as an example how to extend this method
        # easy will be bound to Decorator if defining easy = Decorator.easy in subclass

        return cls.easy_callable(*args, **kwargs)

    def __init__(self, decorated):
        super().__init__()
        self._decorated = decorated

    @property
    def decorated(self):
        decorated = self._decorated
        if isinstance(decorated, contextvars.ContextVar):
            decorated = decorated.get()
        return decorated

    def __getattr__(self, item):
        return getattr(self.decorated, item)

        # yield from self.decorated._marshmallow_field_kwargs

    def descendant_of(self, ancestors: typing.Set['DecoratorBase']):

        if self.__class__ in ancestors:
            # Trying to copy the set
            new_ancestor = ancestors - set((self.__class__,))
            ancestors = new_ancestor

        if not hasattr(self.decorated, 'descendant_of'):
            # TODO: risky, skipped for AttributeError occurring in attribute getter
            return len(ancestors) == 0
        else:
            return self.decorated.descendant_of(ancestors)

    import_required = False
    export_required = False

    is_root = False

    @property
    def graphql_object_type(self):
        typ = list(self._graphql_object_type)
        assert len(typ) != 0

        def op(typ):
            base = typ[0]
            for elem in typ[1:]:
                base = elem(base)
            return base

        return whichever_order(typ, op)

# _vals_

# class BindClass_(DecoratorBase):
#
#     @property
#     def parent(self):
#         return self._bound_cls
#
#     @property
#     def name(self):
#         return self.__attr_name
#
#     def __init__(self, *args, _bound_cls, _attr_name, **kwargs):
#         self.__bound_cls = _bound_cls
#         self.__attr_name = _attr_name
#         super().__init__(*args, **kwargs)
#
#     @property
#     def _bound_cls(self):
#         return self.__bound_cls


class Annotate(DecoratorBase):

    def __init__(self, annotation, *args, decorated, **kwargs):
        if annotation is not None:
            import typing
            if not isinstance(annotation, typing.Type):
                # annotation is a type alias
                # 2 layers max
                if origin := typing.get_origin(annotation):
                    if origin is list:
                        if arguments := typing.get_args(annotation):
                            element_type = next(iter(arguments))
                            if element_type in (str, bool, float, int, ):
                                decorated = List(value=lambda a: a.of_type(element_type), decorated=decorated)
                    else:
                        decorated = OfType(type_cls=origin, decorated=decorated)
            else:
                decorated = OfType(type_cls=annotation, decorated=decorated)

        super().__init__(*args, decorated=decorated, **kwargs)


class BranchHead(DecoratorBase):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self):
        super().__init__(decorated=root_decor)


class Nothing(DecoratorBase):

    """
    Use attr.nothing

    Wrong:
    class A:
      b: int = attr
      c: bool = attr
    A.b and A.c points to the same AttributeBase object, and
        b.name == c.name == 'c'
    """


    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class DefaultValue(DecoratorBase):

    def __init__(self, default_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_value = default_value

    @property
    def default_value(self):
        return self._default_value

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield 'missing', self.default_value

# class DefaultParamsMixin:
#     import_enabled = True
#     export_enabled = True


class ImportRequired(DecoratorBase):

    import_required = True

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield ('required', True)

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class ExportRequired(DecoratorBase):
    # TODO: implement

    export_required = True

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield ('required', True)

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class Required(ImportRequired, ExportRequired):

    @property
    def _graphql_object_type(self):
        import graphql
        # TODO: fix ordering
        yield graphql.GraphQLNonNull
        yield from self.decorated._graphql_object_type
    # pass

class Optional(DecoratorBase):

    import_required = False
    export_required = False

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield 'required', False

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class ImportEnabled(DecoratorBase):
    import_enabled = True

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class ExportEnabled(DecoratorBase):
    export_enabled = True

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class Internal(DecoratorBase):
    is_internal = True
    import_enabled = False
    export_enabled = False

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield 'dump_only', True
        yield 'load_only', True

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class DefaultParamsMixin(ImportEnabled, ExportEnabled, DecoratorBase):
    pass


class OfType(DecoratorBase):

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Dispatch to subclass when required
        """
        target_cls = cls
        if args == (list,):  # TODO: make better
            target_cls = List
        return target_cls(*args, **kwargs)

    def __init__(self, type_cls, *args, **kwargs):
        self._type_cls = type_cls
        super().__init__(*args, **kwargs)

    @property
    def type_cls(self):
        return self._type_cls

    @property
    def _graphql_object_type(self):
        import graphql
        PY_TYPE_MAP_GQL = {
            int: graphql.GraphQLInt,
            bool: graphql.GraphQLBoolean,
            float: graphql.GraphQLFloat,
            str: graphql.GraphQLString,
            list: graphql.GraphQLList
        }
        t = self.type_cls
        if t in PY_TYPE_MAP_GQL:
            yield PY_TYPE_MAP_GQL[t]
        else:
            raise TypeError(f'Failed to locate graphql type for {t.__class__}')
        yield from self.decorated._graphql_object_type

    @property
    def _graphql_field_kwargs(self):
        yield from self.decorated._graphql_field_kwargs
        yield 'type_', self.graphql_object_type

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        from marshmallow import fields as marshmallow_fields
        from datetime import date, time, datetime, timedelta
        PY_TYPE_MARSHMALLOW_FIELD = {
            str: fields.String,
            int: fields.Integer,
            float: fields.Float,
            bool: fields.Boolean,
            date: marshmallow_fields.Date,
            time: marshmallow_fields.Time,
            timedelta: marshmallow_fields.TimeDelta,
            datetime: marshmallow_fields.DateTime
        }
        t = self.type_cls

        if t in PY_TYPE_MARSHMALLOW_FIELD:
            return PY_TYPE_MARSHMALLOW_FIELD[t]
        else:
            return fields.Field
            # raise TypeError(f'Failed to locate marshmallow field def for {t}')


class Pony(DecoratorBase):
    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.is_pony = True
        super().__init__(*args, **kwargs)

    def _make_pony_attribute_cls(self):
        from pony.orm import Discriminator, Required, Optional
        if self.decorated.__class__.__name__ == "Discriminator":
            # TODO: make better
            return Discriminator
        if self.decorated.import_required:
            return Required
        else:
            return Optional

    # @lru_cache(maxsize=None)
    def _make_pony_attribute(self):
        column_name = self.decorated.data_key
        py_type = self.decorated.type_cls
        is_required = self.decorated.import_required
        _pony_attribute_cls = self._make_pony_attribute_cls()
        _pony_attribute = _pony_attribute_cls(
            py_type, is_required=is_required, column=column_name)
        return _pony_attribute

    @cached_property
    def _pony_attribute(self):
        return self._make_pony_attribute()

    @property
    def is_collection(self):
        return self._pony_attribute.is_collection


class String(OfType):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, type_cls=str, **kwargs)


class Str(String):
    pass


class Integer(OfType):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, type_cls=int, **kwargs)


class Int(Integer):
    pass


class IntegerTimestamp(Integer):

    _long_type = None

    @classmethod
    def _get_long_type(cls):
        if not cls._long_type:
            from graphql import GraphQLScalarType
            cls._long_type = GraphQLScalarType('Long')
        return cls._long_type

    @property
    def _graphql_object_type(self):
        yield self._get_long_type()
        yield from self.decorated._graphql_object_type


class Float(OfType):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, type_cls=float, **kwargs)


class Bool(OfType):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, type_cls=bool, **kwargs)

#
# import contextvars
# current_self = contextvars.ContextVar('current_self', default=list())  # TODO: note mutable default
# from contextlib import contextmanager
# @contextmanager
# def use_self(*, self):
#     current_self.get().append(self)
#     try:
#         yield None
#     finally:
#         current_self.get().pop()


_ATTRIBUTE_STORE_NAME = '_attrs'


class Getter(DecoratorBase):

    def _get_default_fget(self, *, name):
        def fget(_self_obj):
            inner = getattr(_self_obj, _ATTRIBUTE_STORE_NAME)
            return getattr(inner, name)
        return fget

    def __init__(self, fget=_NA, *args, **kwargs):
        self._fget = fget
        super().__init__(*args, **kwargs)

    def make_fget(self, name):
        if self._fget is _NA:
            return self._get_default_fget(name=name)
        else:
            return self._fget


class Setter(DecoratorBase):

    def _get_default_fset(self, *, name):
        def fset(_self_obj, value):
            inner = getattr(_self_obj, _ATTRIBUTE_STORE_NAME)
            return setattr(inner, name, value)
        return fset

    def __init__(self, fset=_NA, *args, **kwargs):
        self._fset = fset
        super().__init__(*args, **kwargs)

    def make_fset(self, name):
        if self._fset is _NA:
            return self._get_default_fset(name=name)
        else:
            return self._fset


class Deleter(DecoratorBase):

    def _get_default_fdel(self, *, name):
        def fdel(_self_obj):
            inner = getattr(_self_obj, _ATTRIBUTE_STORE_NAME)
            return delattr(inner, name)
        return fdel

    def __init__(self, fdel=_NA, *args, **kwargs):
        self._fdel = fdel
        super().__init__(*args, **kwargs)

    def make_fdel(self, name):
        if self._fdel is _NA:
            return self._get_default_fdel(name=name)
        else:
            return self._fdel


class InitOptions(DecoratorBase):

    # @property
    # def initializer(self):
    #     return self._initializer

    def __init__(self, initialize, initializer, *args, **kwargs):
        self.initialize = initialize
        self._initializer = initializer
        super().__init__(*args, **kwargs)

    def make_init(self, name=_NA):
        return self._initializer


class Init(InitOptions):

    def __init__(self, initializer=_NA, *args, **kwargs):
        super().__init__(*args, initialize=True, initializer=initializer, **kwargs)


class EasyInit(Init):

    def make_init(self, name=_NA):
        def _init(_self_obj):
            inner = getattr(_self_obj, _ATTRIBUTE_STORE_NAME)
            return setattr(inner, name, self._easy_initializer(_self_obj))
        return _init

    def __init__(self, easy_initializer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._easy_initializer = easy_initializer



class Dict(Init):

    def __init__(self, *args, **kwargs):
        def _dict_initializer(_self):
            attr_name = self.name  # TODO: fix
            setattr(_self, attr_name, dict())
        super().__init__(
            *args,
            initializer=_dict_initializer,
            **kwargs)


class List(OfType):

    def __init__(self, value, *args, **kwargs):
        self._list_value = value
        super().__init__(*args, type_cls=list, **kwargs)

    @property
    def list_value(self):
        return self._list_value

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        # TODO: fix peer
        ins = self.list_value.properties._marshmallow_field_constructor(self.list_value.properties)
        yield ('cls_or_instance', ins)

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        return fields.List

    @property
    def _graphql_object_type(self):
        import graphql
        yield graphql.GraphQLList(
            self.list_value.properties.graphql_object_type
        )
        yield from self.decorated._graphql_object_type


class Enum(OfType):

    from enum import Enum as _Enum

    def __init__(self, enum_cls: typing.Type[_Enum], *args, **kwargs):
        self._enum_cls = enum_cls
        super().__init__(*args, type_cls=str, **kwargs)

    @property
    def _graphql_object_type(self):
        import graphql
        yield graphql.GraphQLEnumType(
            self._enum_cls.__name__,
            values=self._enum_cls
        )
        yield from self.decorated._graphql_object_type


class AttributeName(DecoratorBase):

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield ('attribute', self.name)

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)


class ParentKlass(DecoratorBase):

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)


class DocId(DecoratorBase):

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Dispatch to subclass when required
        """
        def fget(self):
            return self.doc_ref.id

        inner = Getter(fget, *args, **kwargs)
        return cls(decorated=inner)

    @property
    def _graphql_object_type(self):
        import graphql
        yield graphql.GraphQLNonNull(graphql.GraphQLID)
        yield from self.decorated._graphql_object_type

    @property
    def _graphql_field_kwargs(self):
        yield from self.decorated._graphql_field_kwargs
        yield 'type_', self.graphql_object_type

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        return fields.DocIdField



class NodeId(DecoratorBase):
    """
    For GraphQL ID
    """

    @property
    def _graphql_object_type(self):
        import graphql
        yield graphql.GraphQLNonNull(graphql.GraphQLID)
        yield from self.decorated._graphql_object_type

    @property
    def _graphql_field_kwargs(self):
        yield from self.decorated._graphql_field_kwargs
        yield 'type_', self.graphql_object_type

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_property(*args, **kwargs)


class DataKey(DecoratorBase):

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield ('data_key', self.data_key)

    @property
    def data_key(self):
        data_key = self._data_key
        if data_key is not None:
            return self._data_key
        else:
            raise AttributeError

    def __init__(self, data_key=_NA, *args, **kwargs):
        self._data_key = data_key
        super().__init__(*args, **kwargs)


class DataKeyFromName(DataKey):

    @classmethod
    def easy(cls, *args, **kwargs):
        return cls.easy_callable(*args, **kwargs)

    @property
    def data_key(self):
        return self._transformation(self.name)

    def __init__(self, *args, transformation=_NA, **kwargs):
        if transformation is _NA:
            from onto.utils import camel
            transformation = camel
        self._transformation = transformation
        super().__init__(*args, **kwargs)


class NoneAsMissing(DecoratorBase):

    @property
    def _marshmallow_field_override(self):
        yield from self.decorated._marshmallow_field_override
        def _deserialize(_self, value, attr, data, **kwargs):
            if value is None:
                from marshmallow.fields import missing_
                return missing_
            else:
                return super(_self.__class__, _self)._deserialize(value, attr, data, **kwargs)
        yield ('_deserialize', _deserialize)

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield 'allow_none', True


class Embed(OfType):

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield 'obj_type', self.type_cls
        yield 'allow_none', True  # TODO: make better

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        return fields.Embedded

    @property
    def _graphql_object_type(self):
        type_cls = self.type_cls
        if isinstance(type_cls, str):
            from onto.models.meta import ModelRegistry
            type_cls = ModelRegistry.get_cls_from_name(obj_type_str=type_cls)
        # from onto.models.utils import _graphql_object_type_from_attributed_class
        yield type_cls.get_graphql_object_type(is_input=self.is_input)
        yield from self.decorated._graphql_object_type

    # @property
    # def _graphql_(self):
    #     e_cls = attr.type_cls
    #     e_graphql = _graphql_object_type_from_attributed_class(e_cls)
    #     field = field_base(
    #         type_=f(e_graphql),
    #         description=attr.doc
    #     )
    #     return attr.data_key, field


class Set(DecoratorBase):

    def __init__(self, value, *args, **kwargs):
        self.value = value
        super().__init__(*args, **kwargs)


class ReferenceSet(Set):

    def __init__(self, value, *args, **kwargs):
        self.value = value
        super().__init__(*args, **kwargs)

    @property
    def _pony_field(self):
        raise NotImplementedError


class ReferenceList(List):
    pass


class WithReference(DecoratorBase):
    pass


class Relation(DecoratorBase):

    @property
    def _marshmallow_field_kwargs(self):
        yield from self.decorated._marshmallow_field_kwargs
        yield ('dm_cls', self.dm_cls)

    def __init__(self, dm_cls, *args, **kwargs):
        self.dm_cls = dm_cls
        super().__init__(*args, **kwargs)

    @property
    def _marshmallow_field_cls(self):
        from onto.mapper import fields
        return fields.Relationship


class GraphqlCapable(DecoratorBase):

    def __init__(self, *args, is_input, **kwargs):
        self.is_input = is_input
        super().__init__(*args, **kwargs)

    @property
    def _graphql_field_kwargs(self):
        yield from ()


class Doc(DecoratorBase):
    """
    Documented with str
    """

    def __init__(self, doc, *args, **kwargs):
        self._doc = doc
        super().__init__(*args, **kwargs)

    @property
    def doc(self):
        return self._doc

    @property
    def _graphql_field_kwargs(self):
        yield from self.decorated._graphql_field_kwargs
        yield 'description', self.doc


class AsRoot(DecoratorBase):

    is_root = True

