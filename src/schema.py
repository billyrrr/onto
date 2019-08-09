from src import fields
from marshmallow import Schema, post_load
from inflection import camelize, underscore
from functools import partial


attr_name_to_firestore_key = partial(camelize, uppercase_first_letter=False)
firestore_key_to_attr_name = underscore


def _get_field(variable_key, variable_val) -> fields.Field:
    if isinstance(variable_val, int):
        return fields.Integer(
            load_from=attr_name_to_firestore_key(variable_key)
        )
    else:
        # TODO: implement _get_field for other field types
        raise NotImplementedError


def _get_field_vars(vars_obj, fd) -> dict:
    field_vars = dict()
    for key, val in vars_obj.items():
        if key in fd:
            field_vars[key] = _get_field(key, val)
    return field_vars


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
        for k, v in data.items():
            if k in fd:
                key, value = firestore_key_to_attr_name(k), v
                setattr(self.obj, key, value)
        return self.obj

    field_vars = _get_field_vars(vars(obj_cls), fd)

    TempSchema = type("TempSchema", (Schema,),
                      {
                          "__init__": constructor,
                          "make_temp_obj": make_temp_obj,
                          **field_vars
                      }
    )

    return TempSchema(obj_cls)

