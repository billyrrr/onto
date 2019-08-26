import warnings
from collections import Iterable

from marshmallow import MarshalResult
from marshmallow.utils import is_iterable_but_not_string

from .schema import generate_schema
from .model_registry import BaseRegisteredModel
from importlib import import_module


class Serializable(BaseRegisteredModel):

    _fields = None
    _schema_cls = None
    _schema_obj = None

    # _registry = dict()  # classname: cls

    def __init__(self, *args, **kwargs):
        pass

    @property
    def schema_obj(self):
        if self._schema_obj is None:
            self._schema_obj = self._schema_cls()
        return self._schema_obj

    @property
    def schema_cls(self):
        return self._schema_cls

    @classmethod
    def get_schema_cls(cls):
        return cls._schema_cls

    def __init_subclass__(cls, serializable_fields=None, **kwargs):
        """
        See: https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        :param serializable_fields:
        :param kwargs:
        :return:
        """
        super().__init_subclass__(**kwargs)
        # cls._registry[cls.__name__] = cls
        cls._fields = serializable_fields
        # if cls._schema is None:
        #     cls._schema = generate_schema(cls)

    @classmethod
    def _infer_fields(cls) -> list:
        res = list()

        def is_private_var_name(var_name):
            if len(var_name) == 0:
                raise ValueError
            else:
                return var_name[0] == "_"

        for key, val in cls.__dict__.items():
            if not is_private_var_name(key):
                if not callable(val):
                    res.append(key)

        return res

    @classmethod
    def get_fields(cls) -> list:
        """
        Returns a list of fields that are serialized and deserialized.

        :return:
        """

        if cls._fields is None:
            warnings.warn("Inferring fields to serialize and deserialize "
                          "by variable name. "
                          "serializable_fields should rather " +
                          "be specified. Eg. " +
                          "class SubclassOfViewModel(" +
                          "ViewModel, serializable_fields=['property_a'])")
            return cls._infer_fields()
        else:
            return cls._fields

    # def __new__(cls, *args, **kwargs):
    #
    #     instance = super().__new__(cls, *args, **kwargs)
    #     return instance

    def _export_as_dict(self) -> dict:
        """ Map/dict is only supported at root level for now
        TODO: implement iterable support
        :return:
        """
        mres: MarshalResult = self.schema_obj.dump(self)
        d = mres.data

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

    def _import_properties(self, d: dict) -> None:
        """ TODO: implement iterable support
        TODO: test
        TODO: note that this method is not well-tested and most likely
                will fail for nested structures

        :param d:
        :return:
        """
        deserialized = self.schema_obj.load(d).data

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

    def to_dict(self):
        return self._export_as_dict()

    def _export_as_view_dict(self) -> dict:
        """
        TODO: implement iterable support
        :return:
        """

        mres: MarshalResult = self.schema_obj.dump(self)
        d = mres.data

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

    @classmethod
    def from_dict(cls, d, **kwargs):
        instance = cls(**kwargs)  # TODO: fix unexpected arguments
        instance._import_properties(d)
        return instance
