from flask_boiler.models.utils import _schema_cls_from_attributed_class
from flask_boiler.registry import ModelRegistry


# DEFAULT_FIELDS = {"obj_type", "doc_id", "doc_ref"}


class SerializableMeta(ModelRegistry):
    """
    Metaclass for serializable models.
    """

    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)
        attributed = _schema_cls_from_attributed_class(cls=klass)

        if attributed is not None:
            klass._schema_cls = attributed
        # if hasattr(klass, "Meta"):
        #     Moves Model.Meta.schema_cls to Model._schema_cls
        meta = klass.Meta
        if hasattr(meta, "schema_cls"):
            klass._schema_cls = meta.schema_cls


            # if hasattr(meta, "default_fields"):
            #     default_fields = meta.default_fields
            #     if default_fields > DEFAULT_FIELDS:
            #         raise ModelDeclarationError(
            #             f"default_fields argument: {default_fields} "
            #             f"in {name}.Meta is not a subset (<=) of "
            #             f"{DEFAULT_FIELDS} "
            #         )
            #     klass._default_fields = default_fields

        return klass
