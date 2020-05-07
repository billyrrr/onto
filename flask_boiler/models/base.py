from flask_boiler.business_property_store import SimpleStore
from .meta import SerializableMeta
from ..registry import ModelRegistry
from .mixin import Importable, NewMixin, Exportable
from .utils import _collect_attrs
from flask_boiler.schema import Schema


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
    """

    _schema_obj = None
    _schema_cls = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    # self._schema_obj = self._schema_cls()

    @classmethod
    def get_schema_cls(cls):
        """ Returns the Schema class associated with the model class.
        """
        return cls._schema_cls

    @classmethod
    def get_schema_obj(cls):
        """ Returns an instantiated object for Schema associated
                with the model class
        """
        # Use __dict__ to avoid reading from super class
        if "_schema_obj" not in cls.__dict__:
            cls._schema_obj = cls.get_schema_cls()()
        return cls._schema_obj

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
            key: val for key, val in fd.items() if key not in {"doc_id", "doc_ref"}
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


class Serializable(Mutable, metaclass=SerializableMeta):

    class Meta:
        pass
    #     """
    #     Options object for a Serializable model.
    #     """
    #     schema_cls = None

    _schema_base = Schema

    def _init__attrs(self):
        self._attrs = SimpleStore()
        for key, attr in _collect_attrs(cls=self.__class__):
            if attr.initialize:
                attr.initializer(self)

    def __init__(self, *args, **kwargs):
        self._init__attrs()
        super().__init__(*args, **kwargs)
