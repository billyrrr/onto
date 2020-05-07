from typing import Iterable, Tuple

from flask_boiler.attrs import AttributeBase


def _make_schema_name(cls):
    return f"_{cls.__name__}_GeneratedSchema"


def _schema_cls_from_attributed_class(cls):
    """ Make schema from a class containing AttributeBase+ objects

    :return:
    """
    d = dict()
    for key, attr in _collect_attrs(cls):
        field = attr._make_field()
        d[key] = field
    if len(d) == 0:
        return None

    d["Meta"] = type(
        "Meta",
        tuple(),
        {
            "exclude": getattr(cls.Meta, "exclude", tuple())
        })

    if hasattr(cls.Meta, "case_conversion"):
        d["case_conversion"] = cls.Meta.case_conversion

    schema_base = cls._schema_base

    TempSchema = type(_make_schema_name(cls), (schema_base,), d)

    return TempSchema


def _collect_attrs(cls) -> Iterable[Tuple[str, AttributeBase]]:
    """
    Collect all AttributeBase+ objects in the class and its ancestors.

    :param cls:
    :return:
    """
    for key in dir(cls):
        if issubclass(getattr(cls, key).__class__, AttributeBase):
            yield (key, getattr(cls, key))
