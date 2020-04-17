from typing import Iterable, Tuple

from flask_boiler.attrs import AttributeBase
from flask_boiler.schema import Schema


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
    tmp_schema = Schema.from_dict(d, name=_make_schema_name(cls))
    return tmp_schema


def _collect_attrs(cls) -> Iterable[Tuple[str, AttributeBase]]:
    """
    Collect all AttributeBase+ objects in the class and its ancestors.

    :param cls:
    :return:
    """
    for key in dir(cls):
        if issubclass(getattr(cls, key).__class__, AttributeBase):
            yield (key, getattr(cls, key))
