from src import fields
from marshmallow import Schema, post_load
from inflection import camelize, underscore


attr_name_to_firestore_key = camelize
firestore_key_to_attr_name = underscore


def generate_schema(obj) -> Schema:
    """
    Generates
    :param obj:
    :return:
    """

    def constructor(self, obj):
        Schema.__init__(self)
        self.obj = obj

    @post_load
    def make_temp_obj(self, data: dict, **kwargs):
        for k, v in data.items():
            key, value = firestore_key_to_attr_name(k), v
            setattr(self.obj, key, value)
        return self.obj

    TempSchema = type("TempSchema", (Schema,),
                      {
                          "__init__": constructor,
                          "int_a": fields.Integer(load_from="intA"),
                          "int_b": fields.Integer(load_from="intB"),
                          "make_temp_obj": make_temp_obj
                      }
    )

    return TempSchema(obj)

