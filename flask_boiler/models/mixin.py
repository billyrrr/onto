from typing import Optional, Dict

from marshmallow.utils import is_iterable_but_not_string

from flask_boiler import fields, errors
from flask_boiler.context import Context as CTX
from flask_boiler.helpers import EmbeddedElement
# from .base import BaseRegisteredModel, Serializable
from .meta import ModelRegistry


class Importable:
    """
    When object subclass this mixin class, the object has the ability to
        be deserialized/loaded/set from a dictionary.
    """

    @classmethod
    def _import_val(cls, val, **kwargs):
        """ IMPORTANT! Note that the code may fail and result in
                infinite call chain when there is a circular reference.
                The code is not designed to fail this way, but
                    accidental changes to code may make this behavior
                    possible.

        :param val:
        :param to_get:
        :param kwargs:
        :return:
        """

        def embed_element(val: EmbeddedElement):
            d = val.d
            obj_type = d["obj_type"]
            obj_cls = ModelRegistry.get_cls_from_name(obj_type)
            data = {key: val for key, val in d.items() if key != "obj_type"}
            obj = obj_cls.from_dict(d=data)
            return obj

        if isinstance(val, EmbeddedElement):
            return embed_element(val)
        elif is_iterable_but_not_string(val):
            if isinstance(val, list):
                val_list = [cls._import_val(elem, **kwargs)
                            for elem in val]
                return val_list
            elif isinstance(val, dict):
                val_d = dict()
                for k, v in val.items():
                    val_d[k] = cls._import_val(v, **kwargs)
                return val_d
            else:
                raise NotImplementedError

        else:
            return val

    def update_vals(self,
                    with_dict: Optional[Dict] = None,
                    with_raw: Optional[Dict] = None,
                    **kwargs) -> None:
        """ Update values of the object in batch.

        :param with_dict:  Update object with keys and values in the
            with_dict.
        :param with_raw: Do field deserialization before setting
            value of attributes.
        :param kwargs:
        """

        if with_dict is None:
            with_dict = dict()
        if with_raw is not None:
            d = self.get_schema_obj().load(with_raw)
            with_dict = {
                key: self._import_val(val, to_get=False)
                for key, val in d.items()
            }
        kwargs_new = {**with_dict, **kwargs}
        for key, val in kwargs_new.items():
            setattr(self, key, val)

    @classmethod
    def from_dict(cls, d, to_get=True, must_get=False, transaction=None,
                  **kwargs):
        super_cls, obj_cls = cls, cls

        if "obj_type" in d:
            obj_type = d["obj_type"]
            obj_cls = ModelRegistry.get_cls_from_name(obj_type)

            if obj_cls is None:
                raise ValueError("Cannot read obj_type: {}. "
                                 "Make sure that obj_type is a subclass of {}. "
                                 .format(obj_type, super_cls))

        d = obj_cls.get_schema_obj().load(d)

        def apply(val):
            if isinstance(val, dict):
                return {k: obj_cls._import_val(
                    v)
                    for k, v in val.items()
                }
            elif isinstance(val, list):
                return [obj_cls._import_val(
                    v)
                    for v in val]
            else:
                return obj_cls._import_val(
                    val)

        d = {
            key: apply(val)
            for key, val in d.items() if val != fields.allow_missing
        }

        instance = obj_cls.new(**d, **kwargs)  # TODO: fix unexpected arguments
        return instance


class Exportable:
    """
    When object subclass this mixin class, the object has the ability to
        be serialized/dumped/output into a dictionary.
    """

    def _export_val(self, val, to_save=False):
        """
        Private method for serializing an instance variable of the object.
        TODO: test nested

        :param val:
        :param to_save: If set to True, the changes made to an
                    object referenced by master object in
                    a relationship field will be saved. Otherwise,
                    changes are not saved, and the
                    TODO: Add support for atomicity
        """

        def embed_element(val: EmbeddedElement):
            obj = val.obj
            return self._export_val(obj)

        from .base import Serializable
        # if isinstance(val, Serializable):
        #     return val._export_as_dict(to_save=to_save)
        if isinstance(val, EmbeddedElement):
            return embed_element(val)
        elif is_iterable_but_not_string(val):
            if isinstance(val, list):
                val_list = [self._export_val(elem, to_save) for elem in val]
                return val_list
            elif isinstance(val, dict):
                val_d = dict()
                for k, v in val.items():
                    val_d[k] = self._export_val(v, to_save)
                return val_d
            else:
                raise NotImplementedError
        else:
            return val

    def _export_as_dict(self, to_save=False, **kwargs) -> dict:
        """ Map/dict is only supported at root level for now

        """
        d = self.schema_obj.dump(self)

        # print("----")
        # print(d)

        res = dict()
        for key, val in d.items():
            res[key] = self._export_val(val, to_save=to_save, **kwargs)

        return res

    def _export_val_view(self, val):

        def embed_element(val: EmbeddedElement):
            obj = val.obj
            return obj._export_as_view_dict()

        from .base import Serializable
        if isinstance(val, Serializable):
            return val._export_as_view_dict()
        if isinstance(val, EmbeddedElement):
            return embed_element(val)
        elif is_iterable_but_not_string(val):
            if isinstance(val, list):
                val_list = [self._export_val_view(elem) for elem in val]
                return val_list
            elif isinstance(val, dict):
                val_d = dict()
                for k, v in val.items():
                    val_d[k] = self._export_val_view(v)
                return val_d
            else:
                raise NotImplementedError
        else:
            return val

    def _export_as_view_dict(self) -> dict:
        """ Export as dictionary representable to front end.

        """
        d = self.schema_obj.dump(self)

        res = dict()
        for key, val in d.items():
            if key not in self.schema_cls._get_reserved_fieldnames():
                res[key] = self._export_val_view(val)

        return res

    def to_dict(self):
        return self._export_as_dict()


class NewMixin:
    """
    Mixin class for initializing instance variable on creation.
    """

    @classmethod
    def new(cls, allow_default=True, **kwargs):
        """ Instantiates a new instance to the model.

        This is similar to the use of "new" in Java. It is recommended that
        you use "new" to initialize an object, rather than the native
        initializer. Values are initialized based on the order that they are
        declared in the schema.

        :param allow_default: if set to False, an error will be
            raised if value is not provided for a field.
        :param kwargs: keyword arguments to pass to the class
            initializer.
        :return: the instance created
        """

        fd = cls._get_fields()  # Calls classmethod

        # field_keys = {key for key, field in fd.items() }

        _with_dict = dict()

        for key, field in cls._get_fields().items():
            if field.dump_only:
                continue
            if key in kwargs:
                _with_dict[key] = kwargs[key]
            else:
                if field.required:
                    raise errors.DefaultNotAllowedError
                v = field.default_value
                if v != fields.allow_missing:
                    _with_dict[key] = v

        kwargs_keys = set(kwargs.keys())
        keys_super = kwargs_keys - set(_with_dict.keys())

        d_super = {key: kwargs[key] for key in keys_super}

        return cls(_with_dict=_with_dict, **d_super)

    def __init__(self, _with_dict=None, **kwargs):
        """ Private initializer; do not call directly.
            Use "YourModelClass.new(...)" instead.

        :param _with_dict:
        :param kwargs:
        """
        if _with_dict is None:
            _with_dict = dict()
        # TODO: note that obj_type and other irrelevant fields are set; fix
        for key, val in _with_dict.items():
            try:
                setattr(self, key, val)
            except AttributeError as ae:
                CTX.logger.error(f"Error encounntered while setting key: {key}"
                                 f" and value: {val}."
                                 f" with_dict: {_with_dict}. "
                                 f"Error: {ae.args}")
                raise ae
            # elif isinstance(getattr(self.__class__, key), property):
            #     setattr(self, key, val)

        super().__init__(**kwargs)
