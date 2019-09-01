"""
Note that test setup is UNRELIABLE.
Class may persist in registry (of metaclass) across tests.

"""

from flask_boiler import serializable
from flask_boiler import view_model, schema, fields


def test_cls_factory():

    class ModelASchema(schema.Schema):

        int_a = fields.Integer(load_from="intA", dump_to="intA")
        int_b = fields.Integer(load_from="intB", dump_to="intB")

    ModelA = serializable.SerializableClsFactory.create(name="ModelA", schema=ModelASchema)

    obj: ModelA = ModelA()

    assert obj.int_a == 0
    assert obj.int_b == 0

    obj.int_a = 1
    obj.int_b = 2

    assert obj.int_a == 1
    assert obj.int_b == 2

    assert obj.to_dict() == {
        "intA": 1,
        "intB": 2,
        "obj_type": "ModelA"
    }


def test_from_dict():

    class ModelASchema(schema.Schema):

        int_a = fields.Integer(load_from="intA", dump_to="intA")
        int_b = fields.Integer(load_from="intB", dump_to="intB")

    ModelA = serializable.SerializableClsFactory.create(name="ModelA", schema=ModelASchema)

    obj = ModelA.from_dict( {
        "intA": 1,
        "intB": 2,
        "obj_type": "ModelA"
    })

    assert isinstance(obj, ModelA)
    assert obj.int_a == 1
    assert obj.int_b == 2


def test__additional_fields():
    class ModelASchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    class ModelAASchema(ModelASchema):
        int_aa = fields.Integer(load_from="intAA", dump_to="intAA")

    ModelA = serializable.SerializableClsFactory.create(
        name="ModelA",
        schema=ModelASchema
    )

    obj_a = ModelA()

    assert hasattr(obj_a, "int_a")
    assert not hasattr(obj_a, "int_aa")

    ModelAA = serializable.SerializableClsFactory.create(
        name="ModelAA",
        schema=ModelAASchema
    )
    obj_aa = ModelAA()
    assert hasattr(obj_aa, "int_a")
    assert hasattr(obj_aa, "int_aa")


def test_default_value():
    class ModelASchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    ModelA = serializable.SerializableClsFactory.create(
        name="ModelA",
        schema=ModelASchema
    )

    obj_a = ModelA()

    assert obj_a.int_a == 0


def test_property_fields():

    class ModelASchema(schema.Schema):
        some_property = fields.Function(dump_only=True)

    def fget(self):
        return 8

    sp = property(fget=fget)

    ModelA = serializable.SerializableClsFactory.create(
        name="ModelA",
        schema=ModelASchema
    )

    ModelA.some_property = sp

    obj_a = ModelA()

    assert obj_a.some_property == 8


def test_multiple_inheritance():
    class ModelASchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    class ModelBSchema(schema.Schema):
        int_b = fields.Integer(load_from="intB", dump_to="intB")

    class ModelABSchema(ModelASchema, ModelBSchema):
        pass

    ModelAB = serializable.SerializableClsFactory.create(
        name="ModelAB",
        schema=ModelABSchema
    )

    ab = ModelAB()
    ab.int_a = 1
    ab.int_b = 2

    assert ab.int_a == 1
    assert ab.int_b == 2

    assert ab._export_as_dict().items() >= {
        "intA": 1,
        "intB": 2
    }.items()


def test__export_as_dict():
    class ModelASchema(schema.Schema):

        int_a = fields.Integer(load_from="intA", dump_to="intA")
        int_b = fields.Integer(load_from="intB", dump_to="intB")

    ModelA = serializable.SerializableClsFactory.create(
        name="ModelA",
        schema=ModelASchema
    )

    a = ModelA()
    a.int_a = 1
    a.int_b = 2

    assert a._export_as_dict() == {
        "intA": 1,
        "intB": 2,
        "obj_type": "ModelA"
    }


def test_separate_class():
    """
    Tests experimental code for decorator pattern implementation

    :return:
    """

    class ModelASchema(schema.Schema):
        int_a = schema.fields.Integer(load_from="intA", dump_to="intA")
        int_b = schema.fields.Integer(load_from="intB", dump_to="intB")

    class ModelASerializable(serializable.Serializable):
        _schema_cls = ModelASchema

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class ModelAModel(object):

        def __init__(self):
            self.int_a = 0
            self.int_b = 0

    class ModelA(ModelAModel, ModelASerializable):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    a = ModelA()
    a.int_a = 1
    a.int_b = 2

    assert a._export_as_dict() == {
        "intA": 1,
        "intB": 2,
        "obj_type": "ModelA"
    }

