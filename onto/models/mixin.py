from typing import Optional, Dict

from marshmallow.utils import is_iterable_but_not_string

from onto import errors
from onto.mapper import fields
from onto.context import Context as CTX
from onto.mapper.helpers import EmbeddedElement
from ..common import _NA
from ..database import Snapshot
from ..registry import ModelRegistry


def resolve_obj_cls(*, cls, d):
    super_cls, obj_cls = cls, cls

    from onto.common import read_obj_type
    obj_type_str = read_obj_type(d, obj_cls)
    # Note: "obj_type" is NOT the "attribute" property
    # of obj_type field instance

    if obj_type_str is not None:
        """ If obj_type string is specified, use it instead of cls supplied 
            to from_dict. 

        TODO: find a way to raise error when obj_type_str reading 
            fails with None and obj_type evaluates to cls supplied 
            to from_dict unintentionally. 

        """
        obj_cls = ModelRegistry.get_cls_from_name(obj_type_str)
        if obj_cls is None:
            """ If obj_type string is specified but invalid, 
                throw a ValueError. 
            """
            raise ValueError("Cannot read obj_type string: {}. "
                             "Make sure that obj_type is a subclass of {}."
                             .format(obj_type_str, super_cls))

    return obj_cls


class Importable:
    """
    When object subclass this mixin class, the object has the ability to
        be deserialized/loaded/set from a dictionary.
    """

    @classmethod
    def _import_val(cls, val, partial=False, **kwargs):
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
            obj_cls = val.obj_cls
            # data = {key: val for key, val in d.items()}
            obj = obj_cls.from_dict(d=d, partial=partial)
            return obj

        if isinstance(val, EmbeddedElement):
            return embed_element(val)
        elif is_iterable_but_not_string(val):
            if isinstance(val, list):
                val_list = [cls._import_val(elem, partial=partial, **kwargs)
                            for elem in val]
                return val_list
            elif isinstance(val, dict):
                val_d = dict()
                for k, v in val.items():
                    val_d[k] = cls._import_val(v, partial=partial, **kwargs)
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
                key: self._import_val(val)
                for key, val in d.items()
            }
        kwargs_new = {**with_dict, **kwargs}
        for key, val in kwargs_new.items():
            setattr(self, key, val)

    @classmethod
    def _import_from_dict(cls, d, **kwargs):
        return cls._import_val(d, **kwargs)

    @classmethod
    def from_dict(cls, d, transaction=_NA, partial=False, **kwargs):

        obj_cls = resolve_obj_cls(cls=cls, d=d)

        schema_obj = obj_cls.get_schema_obj()
        d = schema_obj.load(d, partial=partial)

        d = cls._import_from_dict(d, partial=partial, transaction=transaction)

        instance = obj_cls.new(**d, **kwargs)  # TODO: fix unexpected arguments
        return instance

    @classmethod
    def from_dict_special(cls, d, **kwargs):
        from onto.models.utils import _collect_attrs

        def y(klass):
            for key, attr in _collect_attrs(klass):
                from onto.attrs.unit import MonadContext
                with MonadContext.context().attribute_name(key).data_key_from_name():
                    if attr.descendant_of(('doc_id',)):
                        yield attr.properties.data_key, attr.name

        special_fields = dict(y(cls))
        m = {
            special_fields[k]: d[k]
            for k, v in d.items()
            if k in special_fields
        }
        d = {
            k:v
            for k, v in d.items()
            if k not in special_fields
        }
        return cls.from_dict(d=d, **m, **kwargs)



class Exportable:
    """
    When object subclass this mixin class, the object has the ability to
        be serialized/dumped/output into a dictionary.
    """

    def _export_val(self, val, **kwargs):
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
            if obj is None:
                return None
            return obj._export_as_dict(**kwargs)  # TODO: remove to_save from elsewhere

        if isinstance(val, EmbeddedElement):
            return embed_element(val)
        elif is_iterable_but_not_string(val):
            if isinstance(val, list):
                val_list = [self._export_val(elem, **kwargs) for elem in val]
                return val_list
            elif isinstance(val, dict):
                val_d = dict()
                for k, v in val.items():
                    val_d[k] = self._export_val(v, **kwargs)
                return val_d
            else:
                raise NotImplementedError
        else:
            return val

    def _export_as_dict(self, **kwargs) -> dict:
        """ Map/dict is only supported at root level for now

        """
        d = self.schema_obj.dump(self)
        return self._export_val(val=d, **kwargs)

    def _export_val_view(self, val):

        def embed_element(val: EmbeddedElement):
            obj = val.obj
            return obj._export_as_view_dict()

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

    # def _export_as_view_dict(self) -> dict:
    #     """ Export as dictionary representable to front end.
    #
    #     """
    #     d = self.schema_obj.dump(self)
    #     for key in self.schema_cls._get_reserved_fieldnames():
    #         _ = d.pop(key, None)
    #
    #     return self._export_val_view(d)

    def to_dict(self):
        return self._export_as_dict()

    def to_snapshot(self):
        return Snapshot(**self._export_as_dict())

    # def to_view_dict(self):
    #     return self._export_as_view_dict()


def is_pony(*, klass):
    try:
        from pony.orm.core import Entity
        return issubclass(klass, Entity)
    except ImportError:
        return False


class NewMixin:
    """
    Mixin class for initializing instance variable on creation.
            Needs to be top level.
            Example:
                 SomeClass(..., SomeBase, NewMixin, object):
                    pass

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

        # fd = cls._get_fields()  # Calls classmethod

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
                v = getattr(field, 'default_value', None)
                if v != fields.allow_missing:
                    _with_dict[key] = v

        kwargs_keys = set(kwargs.keys())
        keys_super = kwargs_keys - set(_with_dict.keys())

        d_super = {key: kwargs[key] for key in keys_super}

        return cls(_with_dict=_with_dict, **d_super)

    def _init_(self, *, _with_dict, _kwargs):
        # TODO: note that obj_type and other irrelevant fields are set; fix
        for key, val in _with_dict.items():
            try:
                setattr(self, key, val)
            except AttributeError as ae:
                CTX.logger.error(f"Error encountered while setting key: {key}"
                                 f" and value: {val}."
                                 f" with_dict: {_with_dict}. "
                                 f"Error: {ae.args}")
                raise ae
            # elif isinstance(getattr(self.__class__, key), property):
            #     setattr(self, key, val)
        # TODO: log and throw with extraneous arguments
        if len(_kwargs) != 0:
            raise ValueError(f'Received extraneous arguments '
                             f'{_kwargs}')
        super().__init__(**_kwargs)

    def _init_pony_(self, *, _with_dict, _kwargs):
        if len(_kwargs) != 0:
            raise ValueError(f'Received extraneous arguments '
                             f'{_kwargs}')
        from onto.models.base import PonyStore
        self._attrs = PonyStore()
        self._attrs._set_owner(self)  # TODO: implement garbage collection
        super().__init__(**_with_dict, **_kwargs)

    def __init__(self, _with_dict=None, **kwargs):
        """ Private initializer; do not call directly.
            Use "YourModelClass.new(...)" instead.
        Needs to be top level

        :param _with_dict:
        :param kwargs:
        """
        if _with_dict is None:
            _with_dict = dict()
        if is_pony(klass=self.__class__):
            self._init_pony_(_with_dict=_with_dict, _kwargs=kwargs)
        else:
            self._init_(_with_dict=_with_dict, _kwargs=kwargs)


