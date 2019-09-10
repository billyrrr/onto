import inspect
import warnings
from typing import TypeVar, Union

from marshmallow.utils import is_iterable_but_not_string

from . import fields
from .model_registry import BaseRegisteredModel
from . import schema


# from abc import ABC, abstractmethod


class SchemedBase(object):

    @property
    def schema_obj(self):
        raise NotImplementedError

    @property
    def schema_cls(self):
        raise NotImplementedError


class Schemed(object):
    _schema_obj = None
    _schema_cls = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._schema_obj = self._schema_cls()

    @classmethod
    def get_schema_cls(cls):
        return cls._schema_cls

    @classmethod
    def get_schema_obj(cls):
        if cls._schema_obj is None:
            cls._schema_obj = cls._schema_cls()
        return cls._schema_obj

    @property
    def schema_cls(self):
        return self.get_schema_cls()

    @property
    def schema_obj(self):
        return self.get_schema_obj()

    @classmethod
    def _get_fields(cls):
        return cls.get_schema_obj().fields
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


class Importable(SchemedBase):

    def _import_properties(self, d: dict) -> None:
        """ TODO: implement iterable support
        TODO: test
        TODO: note that this method is not well-tested and most likely
                will fail for nested structures

        :param d:
        :return:
        """
        deserialized = self.schema_obj.load(d)

        def import_val(val):
            if isinstance(val, dict) and "obj_type" in val:
                # Deserialize nested object
                obj_type = val["obj_type"]
                # TODO: check hierarchy
                #   (_registry is a singleton dictionary and flat for now)
                obj_cls = BaseRegisteredModel.get_subclass_cls(obj_type)

                obj = obj_cls.create(doc_id=val.get("doc_id", None))
                obj._import_properties(val)

            elif is_iterable_but_not_string(val):
                if isinstance(val, list):
                    val_list = [import_val(elem) for elem in val]
                    return val_list
                elif isinstance(val, dict):
                    val_d = dict()
                    for k, v in val.items():
                        val_d[k] = import_val(v)
                    return val_d
                else:
                    raise NotImplementedError

            else:
                return val

        for key, val in deserialized.items():
            # if key not in self.__get_dump_only_fields__():
            setattr(self, key, import_val(val))

    @classmethod
    def from_dict(cls, d, **kwargs):
        instance = cls(**kwargs)  # TODO: fix unexpected arguments
        instance._import_properties(d)
        return instance


class Exportable(SchemedBase):

    def _export_as_dict(self) -> dict:
        """ Map/dict is only supported at root level for now
        TODO: implement iterable support
        :return:
        """
        d = self.schema_obj.dump(self)

        def export_val(val):
            if isinstance(val, Serializable):
                return val._export_as_dict()
            elif is_iterable_but_not_string(val):
                if isinstance(val, list):
                    val_list = [export_val(elem) for elem in val]
                    return val_list
                elif isinstance(val, dict):
                    val_d = dict()
                    for k, v in val.items():
                        val_d[k] = export_val(v)
                    return val_d
                else:
                    raise NotImplementedError
            else:
                return val

        res = dict()
        for key, val in d.items():
            res[key] = export_val(val)

        return res

    def _export_as_view_dict(self) -> dict:
        """
        TODO: implement iterable support
        :return:
        """

        d = self.schema_obj.dump(self)

        def export_val(val):
            if isinstance(val, Serializable):
                return val._export_as_view_dict()
            elif is_iterable_but_not_string(val):
                if isinstance(val, list):
                    val_list = [export_val(elem) for elem in val]
                    return val_list
                elif isinstance(val, dict):
                    val_d = dict()
                    for k, v in val.items():
                        val_d[k] = export_val(v)
                    return val_d
                else:
                    raise NotImplementedError
            else:
                return val

        res = dict()
        for key, val in d.items():
            if key not in self.schema_cls._get_reserved_fieldnames():
                res[key] = export_val(val)

        return res

    def to_dict(self):
        return self._export_as_dict()


def initializer(obj, d):
    for key, val in d.items():
        assert isinstance(val, fields.Field)
        # if not hasattr(obj, key):
        if key not in dir(obj):
            setattr(obj, key, val.default_value)


class AutoInitialized(object):

    @classmethod
    def _get_fields(cls):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initializer(self, self._get_fields())


class Serializable(BaseRegisteredModel,
                   Schemed,
                   Importable,
                   Exportable,
                   AutoInitialized, ):
    pass


T = TypeVar('T')
U = TypeVar('U')


class SerializableClsFactory:

    @classmethod
    def create(cls, name, schema: T, base:U=Serializable) -> Union[T, U]:

        existing = BaseRegisteredModel.get_subclass_cls(name)
        if existing is None:
            new_cls = type(name,  # class name
                           (base, ),
                           dict(
                               _schema_cls=schema
                           )
                           )
            return new_cls
        else:
            return existing
