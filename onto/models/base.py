import functools

from .meta import SerializableMeta, AttributedMeta
from ..registry import ModelRegistry
from .mixin import Importable, NewMixin, Exportable
from .utils import _collect_attrs, _schema_cls_from_attributed_class
from onto.mapper.schema import Schema


class SimpleStore:
    """
    To store simple business properties
    """
    pass


class PonyStore:

    def _set_owner(self, owner):
        self.parent = owner

    def __getattr__(self, item):
        _self = self.parent
        attr = _self._adict_[item]
        inner = _self._vals_
        return inner[attr]


class AttributedMixin(metaclass=AttributedMeta):
    """ helper to declare mixin classes with attributes
    Example:
        class LatLonMixin(AttributedMixin):
            lat = attrs.float
            lon = attrs.float

        class Location(LatLonMixin, DomainModel):
            name = attrs.string

        # Location will have attributes lat, lon, and name.

    """
    @classmethod
    def attrs(cls):
        return cls.__attributes


class BaseRegisteredModel(metaclass=ModelRegistry):
    """
    Ref: https://github.com/faif/python-patterns/blob/master/patterns/behavioral/registry__py3.py
    """

    @classmethod
    def _get_children(cls):
        return {cls.get_cls_from_name(c_str)
                for c_str in cls._get_children_str(cls.__name__)}

    @classmethod
    def _get_subclasses(cls):
        res = {cls, }
        children = cls._get_children()
        for child in children:
            res |= child._get_subclasses()
        return res

    @classmethod
    def _get_subclasses_str(cls):
        return list(
            sorted(_cls.__name__ for _cls in cls._get_subclasses())
        )

    @classmethod
    def _get_parents(cls):
        return {cls.get_cls_from_name(c_str)
                for c_str in cls._get_parents_str(cls.__name__)}

    get_parents = _get_parents
    get_subclasses = _get_subclasses


class SchemedBase:

    @property
    def schema_obj(self):
        raise NotImplementedError

    @property
    def schema_cls(self):
        raise NotImplementedError


class Schemed(SchemedBase):
    """
    A mixin class for object bounded to a schema for serialization
        and deserialization.
    TODO: maybe add caching
    Currently schema is reconstructed at every call to
        refresh value for different contexts.
    """

    _schema_obj = None
    _schema_cls = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    # self._schema_obj = self._schema_cls()

    @classmethod
    @functools.lru_cache(maxsize=None)
    def get_schema_cls(cls):
        """ Returns the Schema class associated with the model class.
        """
        return _schema_cls_from_attributed_class(cls=cls)

    @classmethod
    def get_schema_obj(cls):
        """ Returns an instantiated object for Schema associated
                with the model class
        """
        # Use __dict__ to avoid reading from super class
        # if "_schema_obj" not in cls.__dict__:
        #     schema_cls = cls.get_schema_cls()
        #     if schema_cls is None:
        #         return None
        #     cls._schema_obj = schema_cls()
        # return cls._schema_obj
        _schema_cls = cls.get_schema_cls()
        _schema_obj = _schema_cls()
        return _schema_obj

    @property
    def schema_cls(self):
        """ Returns the Schema class associated with the model object.
        """
        return self.get_schema_cls()

    @property
    def schema_obj(self):
        """ Returns an instantiated object for Schema associated
                with the model object.
        """
        return self.get_schema_obj()

    @classmethod
    def _get_fields(cls):
        fd = cls.get_schema_obj().fields
        return {
            key: val for key, val in fd.items()  # TODO: change
        }

    #     """ TODO: find ways of collecting fields without reading
    #                 private attribute on Marshmallow.Schema
    #
    #     :return:
    #     """
    #     res = dict()
    #     for name, declared_field in cls.get_schema_obj().fields.items():
    #         if not declared_field.dump_only:
    #             res[name] = declared_field
    #     return res


class Mutable(BaseRegisteredModel,
              Schemed, Importable, NewMixin, Exportable):
    pass


class Immutable(BaseRegisteredModel, Schemed, NewMixin, Exportable):
    pass


class GraphqlMixin(BaseRegisteredModel):

    _union = False

    def graphql_field_resolve(self, info: 'GraphQLResolveInfo', *args):
        from graphql import GraphQLResolveInfo
        info: GraphQLResolveInfo
        field_name = info.field_name
        return self.graphql_representation.get(field_name, None)

    import functools

    @property
    @functools.lru_cache(maxsize=None)
    def graphql_representation(self):
        return self.to_dict()

    @staticmethod
    def _convert(key, attr, is_input):
        if not attr.properties.is_internal:
            from onto.attrs.unit import MonadContext
            context = MonadContext.context()
            context = context.graphql_capable(is_input=is_input)
            context = context.attribute_name(key)

            annotation = attr.annotation
            context = context.annotate(annotation)

            context = context.data_key_from_name()
            context = context.optional

            with context:
                return attr.properties.data_key, attr.graphql_field

    @classmethod
    def __fields_gen(cls, is_input):
        for key, attr in _collect_attrs(cls):
            # TODO: check to see if .attribute_name(key).data_key(key) should be removed
            if ret := cls._convert(key=key, attr=attr, is_input=is_input):
                yield ret
        else:
            yield from ()

    @classmethod
    def _get_union_graphql_interface(cls):
        """
        本层
        """
        import graphql

        def resolve_type(__self, value, _type):
            raise NotImplementedError

        fields = lambda: dict(cls.__fields_gen(is_input=is_input))
        type_name = cls.__name__

        ot = graphql.GraphQLInterfaceType(
            name=type_name,
            resolve_type=resolve_type,
            fields=fields,
        )
        return ot

    @classmethod
    def get_graphql_interfaces(cls):
        for parent in cls.get_parents():
            if issubclass(parent, GraphqlMixin):
                yield from parent.get_graphql_interfaces()

        if cls._union:
            yield cls._get_union_graphql_interface()

        yield from ()  # Empty case

    @classmethod
    @functools.lru_cache(maxsize=None)
    def get_graphql_object_type(cls, is_input=False):

        if unwrap := getattr(cls.Meta, "unwrap", None):

            key, attr = next((k, v) for k, v in _collect_attrs(cls) if k == unwrap)
            data_key, graphql_field = cls._convert(key=key, attr=attr, is_input=is_input)

            from graphql import GraphQLScalarType
            assert isinstance(graphql_field.type, GraphQLScalarType)

            this_type = GraphQLScalarType(
                cls.__name__,
                serialize=graphql_field.type.serialize,
                parse_value=graphql_field.type.parse_value,
                parse_literal=graphql_field.type.parse_literal,
            )
            return this_type
        else:
            import graphql
            if not is_input:
                base = graphql.GraphQLObjectType
                type_name = cls.__name__
            else:
                base = graphql.GraphQLInputObjectType
                type_name = f'{cls.__name__}Input'

            fields = lambda: dict(cls.__fields_gen(is_input=is_input))

            ot = base(
                type_name,
                fields=fields
            )
            return ot


class Serializable(Mutable, GraphqlMixin, metaclass=SerializableMeta):

    class Meta:
        pass
    #     """
    #     Options object for a Serializable model.
    #     """
    #     schema_cls = None

    _schema_base = Schema

    def _init__attrs(self):
        if not getattr(self, '_attrs', None):
            self._attrs = SimpleStore()
        from onto.attrs.unit import MonadContext
        with MonadContext.context().init_options(initialize=False, initializer=None):
            for key, attr in _collect_attrs(cls=self.__class__):
                if attr.properties.initialize:
                    initializer = attr.properties.make_init(name=key)
                    initializer(self)

    def __init__(self, *args, **kwargs):
        self._init__attrs()
        super().__init__(*args, **kwargs)
