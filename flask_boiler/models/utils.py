from typing import Iterable, Tuple

from flask_boiler.attrs import AttributeBase


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


def _graphql_field_from_attr(attr):

    from flask_boiler import attrs
    import graphql
    if attr.__class__ is attrs.attribute.EmbeddedAttribute:
        e_cls = attr.obj_type
        e_graphql = _graphql_object_type_from_attributed_class(e_cls)
        field = graphql.GraphQLField(
            type_=e_graphql,
            description=attr.doc
        )
        return field
    elif isinstance(attr, attrs.attribute.AttributeBase):
        import graphql
        TYPE_MAP = {
            int: graphql.GraphQLInt,
            bool: graphql.GraphQLBoolean,
            float: graphql.GraphQLFloat,
            str: graphql.GraphQLString,
            list: graphql.GraphQLList
        }
        field = graphql.GraphQLField(
            type_=TYPE_MAP[attr.type_cls],
            description=attr.doc
        )
        return field
    else:
        raise NotImplementedError


def _graphql_object_type_from_attributed_class(cls):
    """ Make GraphQL schema from a class containing AttributeBase+ objects

    :return:
    """

    # import_only = getattr(cls.Meta, "import_only", False)
    # export_only = getattr(cls.Meta, "export_only", False)

    import graphql

    fields = {
        key: _graphql_field_from_attr(attr)
        for key, attr in _collect_attrs(cls)
    }

    graphql_object_type = graphql.GraphQLObjectType(
        cls.__name__,
        fields=fields
    )

    return graphql_object_type


def _collect_attrs(cls) -> Iterable[Tuple[str, AttributeBase]]:
    """
    Collect all AttributeBase+ objects in the class and its ancestors.

    :param cls:
    :return:
    """
    for key in dir(cls):
        if issubclass(getattr(cls, key).__class__, AttributeBase):
            yield (key, getattr(cls, key))
