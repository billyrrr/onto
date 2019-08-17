import warnings

from . import fields
import marshmallow
from marshmallow import post_load
from inflection import camelize, underscore
from functools import partial

import inspect


def obj_type_serialize(obj: object):
    """ Returns class name. To be used with Schema.obj_type field.

    :param obj:
    :return:
    """

    return obj.__class__.__name__


def obj_type_deserialize(value):
    """ Returns class name. To be used with Schema.obj_type field.

    :param value:
    :return:
    """

    return value


class Schema(marshmallow.Schema):
    """
    Attributes:
    ============
    obj_type: fields.Function
        Exports and imports class name of an instance for differentiating
            different subclasses of PrimaryObject in the same collection.
    """

    obj_type = fields.Function(
        serialize=obj_type_serialize, deserialize=obj_type_deserialize)


attr_name_to_firestore_key = partial(camelize, uppercase_first_letter=False)
firestore_key_to_attr_name = underscore


def _get_field(variable_key) -> fields.Field:
    warnings.warn("_get_field is returning wildcard field")
    return fields.Raw(
            load_from=attr_name_to_firestore_key(variable_key)
        )

    # if isinstance(variable_val, int):
    #     return fields.Integer(
    #         load_from=attr_name_to_firestore_key(variable_key)
    #     )
    # elif isinstance(variable_val, property):
    #
    # else:
    #     # TODO: implement _get_field for other field types
    #     raise NotImplementedError


def _get_field_vars(var_names, fd) -> dict:
    """

    :param var_names: A list of (instance) variable names
    :param fd:
    :return:
    """
    field_vars = dict()
    for var_name in var_names:
        if var_name in fd:
            field_vars[var_name] = _get_field(var_name)
    return field_vars


def _get_instance_variables(obj_cls) -> list:
    """
    Returns a dict of instance variable name: default value
    Note that this method does not work for now
    :param obj_cls:
    :return:
    """
    # init_func: function = obj_cls.__init__
    res = obj_cls.__init__.__code__.co_names
    return list(res)


def generate_schema(obj_cls) -> Schema:
    """
    Generates
    :param obj:
    :return:
    """

    def constructor(self, obj_cls):
        Schema.__init__(self)
        self.obj_cls = obj_cls

    # A list of all fields to serialize and deserialize
    fd = obj_cls.get_fields()

    @post_load
    def make_temp_obj(self, data: dict, **kwargs):
        obj = self.obj_cls()
        for k, v in data.items():
            key, value = firestore_key_to_attr_name(k), v
            if key in fd:
                setattr(obj, key, value)
        return obj

    instance_vars = _get_instance_variables(obj_cls)
    field_vars = _get_field_vars(instance_vars, fd)

    TempSchema = type("TempSchema", (Schema,),
                      {
                          "__init__": constructor,
                          "make_temp_obj": make_temp_obj,
                          **field_vars
                      }
    )

    return TempSchema(obj_cls)

