from flask_boiler.business_property_store import SimpleStore
from flask_boiler.schema import Schema
from flask_boiler.serializable import Serializable
from flask_boiler.attributes import AttributeBase
from typing import Iterable, Tuple


def _make_schema_name(cls):
    return f"_{cls.__name__}_GeneratedSchema"


def _schema_cls_from_attributed_class(cls):
    """ Make schema from a class containing AttributeBase+ objects

    :return:
    """
    if cls._schema_cls is None:
        d = dict()
        for key, attr in _collect_attrs(cls):
            field = attr._make_field()
            d[key] = field
        tmp_schema = Schema.from_dict(d, name=_make_schema_name(cls))
        return tmp_schema
    else:
        return cls._schema_cls


def _collect_attrs(cls) -> Iterable[Tuple[str, AttributeBase]]:
    """
    Collect all AttributeBase+ objects in the class and its ancestors.

    :param cls:
    :return:
    """
    for key in dir(cls):
        if issubclass(getattr(cls, key).__class__, AttributeBase):
            yield (key, getattr(cls, key))


class ModelBase(Serializable):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._schema_cls = _schema_cls_from_attributed_class(cls=cls)

    def __init__(self, *args, **kwargs):
        self._attribute_store = SimpleStore()
        super().__init__(*args, **kwargs)
