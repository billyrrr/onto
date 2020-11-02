from functools import lru_cache
from typing import Iterable, Tuple

from onto.attrs import AttributeBase


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
        field = attr._make_field()
        field.load_only = field.load_only or import_only
        field.dump_only = field.dump_only or export_only
        d[key] = field
    if len(d) == 0:
        return None
    else:
        m_meta = {
            "exclude": getattr(cls.Meta, "exclude", tuple())
        }

        d["Meta"] = type(
            "Meta",
            tuple(),
            m_meta
        )

        if hasattr(cls.Meta, "case_conversion"):
            d["case_conversion"] = cls.Meta.case_conversion

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

    fields = dict(
        _graphql_field_from_attr(attr, input=input)
        for key, attr in _collect_attrs(cls) if not attr.is_internal
    )

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
    for key in dir(cls):
        if issubclass(getattr(cls, key).__class__, AttributeBase):
            attr = getattr(cls, key)
            yield (key, attr)
