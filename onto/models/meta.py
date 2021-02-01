from onto.models.utils import _schema_cls_from_attributed_class
from onto.registry import ModelRegistry


# DEFAULT_FIELDS = {"obj_type", "doc_id", "doc_ref"}



class SerializableMeta(ModelRegistry):
    """
    Metaclass for serializable models.
    """

    @classmethod
    def __collect_attributes(mcs, bases, attrs) -> None:
        attrs['__attributes'] = dict()

        for base in bases:
            if isinstance(base, SerializableMeta):
                attrs['__attributes'] = dict(
                    list(attrs['__attributes'].items()) +
                    list(base.__dict__['__attributes'].items())
                )

        def is_attribute(a):
            from onto.attrs.attribute_new import AttributeBase
            return isinstance(a, AttributeBase) and not a.properties.is_root

        for attr_name, a in list(attrs.items()):
            if is_attribute(a):
                attrs['__attributes'][attr_name] = a
                del attrs[attr_name]

    def __new__(mcs, name, bases, attrs):
        mcs.__collect_attributes(bases, attrs)
        klass = super().__new__(mcs, name, bases, attrs)
        return klass

    def __init__(klass, name, base, ns):
        super().__init__(name, base, ns)

        __attributes = ns['__attributes']

        for attr_name, attr in __attributes.items():
            __attributes[attr_name] = attr.name(attr_name).parent_klass(parent=klass)

        for attr_name, attr in __attributes.items():
            from onto.attrs.unit import MonadContext
            with MonadContext.context().getter().setter().deleter():
                p = property(
                    fget=getattr(attr, 'fget', None),
                    fset=getattr(attr, 'fset', None),
                    fdel=getattr(attr, 'fdel', None),
                    doc=getattr(attr, 'doc', None)
                )
                setattr(klass, attr_name, p)

        meta = klass.Meta
        if hasattr(meta, "schema_cls"):
            klass._schema_cls = meta.schema_cls

        attributed = _schema_cls_from_attributed_class(cls=klass)
        if attributed is not None:
            klass._schema_cls = attributed

        # if hasattr(klass, "Meta"):
        #     Moves Model.Meta.schema_cls to Model._schema_cls


            # if hasattr(meta, "default_fields"):
            #     default_fields = meta.default_fields
            #     if default_fields > DEFAULT_FIELDS:
            #         raise ModelDeclarationError(
            #             f"default_fields argument: {default_fields} "
            #             f"in {name}.Meta is not a subset (<=) of "
            #             f"{DEFAULT_FIELDS} "
            #         )
            #     klass._default_fields = default_fields


