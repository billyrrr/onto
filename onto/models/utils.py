from functools import lru_cache
from typing import Iterable, Tuple

from onto.attrs.attribute_new import AttributeBase


def _make_schema_name(cls):
    return f"_{cls.__name__}_GeneratedSchema"


def _schema_cls_from_attributed_class(cls):
    """ Make schema from a class containing AttributeBase+ objects

    :return:
    """

    import_only = getattr(cls.Meta, "import_only", False)
    export_only = getattr(cls.Meta, "export_only", False)

    d = dict()
    for key, attr in _collect_attrs(cls):
        if key == '_pk_':
            """ ponyorm duplicates primary key field 
            TODO: make better 
            """
            continue

        try:

            from onto.attrs.unit import MonadContext
            context = MonadContext.context()

            context = context.marshmallow_capable_base()

            case_conversion = True
            if hasattr(cls.Meta, "case_conversion"):
                new_case_conversion = cls.Meta.case_conversion
                if new_case_conversion is not None:
                    case_conversion = new_case_conversion

            context = context.name(attr.name).data_key(attr.name)

            annotation = attr.annotation
            context = context.annotate(annotation)

            from onto.utils import camel
            transformation = camel if case_conversion else lambda a: a
            context = context.data_key_from_name(transformation=transformation)

            with context:
                field = attr.marshmallow_field
        except Exception as e:
            raise ValueError(f'Error while making field {key}') from e
        field.load_only = field.load_only or import_only
        field.dump_only = field.dump_only or export_only
        d[key] = field
    if len(d) == 0:
        return None
    else:
        # TODO: note that inheritance of super.Meta replaces Meta completely
        # TODO:     as opposed to cls.Meta = super.Meta + cls.Meta
        if unwrap := getattr(cls.Meta, "unwrap", None):

            from onto.mapper.fields import Field
            field: Field = d[unwrap]
            data_key = field.data_key

            from marshmallow.decorators import pre_load, post_dump
            @pre_load
            def unwrap_field(self, data, many, **kwargs):
                if many:
                    raise ValueError  # TODO: check logics first
                new_data = {
                    data_key: data
                }
                return new_data

            d['unwrap_field'] = unwrap_field

            @post_dump
            def wrap_field(self, data, many, **kwargs):
                if many:
                    raise ValueError  # TODO: check logics first
                return data[data_key]  # TODO: check for key error for read only fields
            d['wrap_field'] = wrap_field

        m_meta = {
            "exclude": getattr(cls.Meta, "exclude", tuple()),
        }

        d["Meta"] = type(
            "Meta",
            tuple(),
            m_meta
        )

        # TODO: make better
        # if hasattr(cls.Meta, "case_conversion"):
        #     d["case_conversion"] = cls.Meta.case_conversion

        schema_base = cls._schema_base if cls._schema_cls is None else cls._schema_cls

        TempSchema = type(_make_schema_name(cls), (schema_base,), d)

        return TempSchema


def _graphql_type_from_py(t: type, input=False):
    import graphql
    PY_TYPE_MAP_GQL = {
        int: graphql.GraphQLInt,
        bool: graphql.GraphQLBoolean,
        float: graphql.GraphQLFloat,
        str: graphql.GraphQLString,
        list: graphql.GraphQLList
    }
    if t in PY_TYPE_MAP_GQL:
        return PY_TYPE_MAP_GQL[t]
    else:
        if input:
            return _graphql_object_type_from_attributed_class(t, input=input)
        else:
            raise ValueError


def _graphql_field_from_attr(attr, input=False):
    import graphql

    if not input:
        field_base = graphql.GraphQLField
    else:
        field_base = graphql.GraphQLInputField

    if hasattr(attr, 'collection') and attr.collection == list:
        f = lambda ot: graphql.GraphQLList(ot)
    else:
        f = lambda ot: ot

    from onto import attrs
    if attr.__class__ is attrs.attribute.EmbeddedAttribute:
        e_cls = attr.type_cls
        e_graphql = _graphql_object_type_from_attributed_class(e_cls)
        field = field_base(
            type_=f(e_graphql),
            description=attr.doc
        )
        return attr.data_key, field
    elif isinstance(attr, attrs.attribute.AttributeBase):
        import graphql
        field = field_base(
            type_=f(_graphql_type_from_py(t=attr.type_cls)),
            description=attr.doc
        )
        return attr.data_key, field
    else:
        raise NotImplementedError


@lru_cache(maxsize=None)  # Cached property
def _graphql_object_type_from_attributed_class(cls, input=False):
    """ Make GraphQL schema from a class containing AttributeBase+ objects

    :return:
    """

    # import_only = getattr(cls.Meta, "import_only", False)
    # export_only = getattr(cls.Meta, "export_only", False)

    import graphql

    from onto.attrs.unit import MonadContext

    def fields_gen():
        for key, attr in _collect_attrs(cls):
            # TODO: check to see if .name(key).data_key(key) should be removed
            if not attr.properties.is_internal:
                from onto.attrs.unit import MonadContext
                context = MonadContext.context()
                context = context.graphql_capable(is_input=input)
                context = context.name(attr.name)

                annotation = attr.annotation
                context = context.annotate(annotation)

                context = context.data_key_from_name()

                with context:
                    yield attr.properties.data_key, attr.graphql_field

    fields = lambda: dict(fields_gen())

    if not input:
        base = graphql.GraphQLObjectType
    else:
        base = graphql.GraphQLInputObjectType

    type_name = cls.__name__

    # TODO: maybe add
    # if input:
    #     type_name += "Input"

    graphql_object_type = base(
        type_name,
        fields=fields
    )

    return graphql_object_type


def _collect_attrs(cls) -> Iterable[Tuple[str, AttributeBase]]:
    """
    Collect all AttributeBase+ objects in the class and its ancestors.
    TODO: debug empty iter of length 0

    :param cls:
    :return:
    """
    import inspect
    from functools import partial

    for key, attr in cls.__attributes.items():
        # if issubclass(getattr(cls, key)):
        #     attr = getattr(cls, key)
        yield key, attr  # attr.bind_class_(_bound_cls=cls, _attr_name=key)
