import warnings

from marshmallow import MarshalResult

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
        """
        TODO: implement iterable support
        :return:
        """
        mres: MarshalResult = self.schema_obj.dump(self)
        d = mres.data

        res = dict()
        for key, val in d.items():
            if isinstance(val, Serializable):
                res[key] = val._export_as_dict()
            else:
                res[key] = val
        return res

    def _import_properties(self, d: dict) -> None:
        """ TODO: implement iterable support

        :param d:
        :return:
        """
        deserialized = self.schema_obj.load(d).data
        for key, val in deserialized.items():
            if isinstance(val, dict) and "obj_type" in val:
                # Deserialize nested object
                obj_type = val["obj_type"]
                # TODO: check hierarchy
                #   (_registry is a singleton dictionary and flat for now)
                BaseRegisteredModel.get_subclass_cls(obj_type)
            else:
                if key != "obj_type":
                    setattr(self, key, val)

    def to_dict(self):
        return self._export_as_dict()

    def _export_as_view_dict(self) -> dict:
        """
        TODO: implement iterable support
        :return:
        """

        mres: MarshalResult = self.schema_obj.dump(self)
        d = mres.data

        res = dict()
        for key, val in d.items():
            if isinstance(val, Serializable):
                res[key] = val._export_as_view_dict()
            else:
                if key != "obj_type":
                    res[key] = val
        return res

    @classmethod
    def from_dict(cls, d, **kwargs):
        instance = cls(**kwargs)  # TODO: fix unexpected arguments
        instance._import_properties(d)
        return instance
