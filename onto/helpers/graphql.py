def default_field_resolver(source, info, **args):
    """Default field resolver.

    If a resolve function is not given, then a default resolve behavior is used which
    takes the property of the source object of the same name as the field and returns
    it as the result, or if it's a function, returns the result of calling that function
    while passing along args and context.

    For dictionaries, the field names are used as keys, for all other objects they are
    used as attribute names.
    """
    # Ensure source is a value for which property access is acceptable.
    field_name = info.field_name
    value = (
        source.get(field_name)
        if isinstance(source, dict)
        else source.graphql_field_resolve(info, **args)
    )
    if callable(value):
        return value(info, **args)
    return value


class GraphqlAttributedMixin:
    from graphql import GraphQLResolveInfo

    def graphql_field_resolve(self, info: GraphQLResolveInfo, *args):
        field_name = info.field_name
        return self.graphql_representation.get(field_name, None)

    import functools

    @property
    @functools.lru_cache(maxsize=None)
    def graphql_representation(self):
        return self.to_dict()
