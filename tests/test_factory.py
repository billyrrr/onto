from flask_boiler import schema, fields, factory


def test_create():

    class ModelASchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    class ModelAASchema(ModelASchema):
        int_aa = fields.Integer(load_from="intAA", dump_to="intAA")

    ModelAA = factory.ClsFactory.create(
        name="ModelAA",
        schema=ModelAASchema
    )

    obj_aa = ModelAA()
    assert hasattr(obj_aa, "int_a")
    assert hasattr(obj_aa, "int_aa")


def test_create_with_new():

    class ModelACSchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    ModelAC = factory.ClsFactory.create_customized(
        name="ModelAC",
        schema=ModelACSchema,
        auto_initialized=False,
        importable=False,
        exportable=True
    )

    obj_a = ModelAC.new(int_a=3)

    assert obj_a.int_a == 3


def test_create_with_new_exportable():

    class ModelACSchema(schema.Schema):
        int_a = fields.Integer(load_from="intA", dump_to="intA")

    ModelAC = factory.ClsFactory.create_customized(
        name="ModelAC",
        schema=ModelACSchema,
        auto_initialized=False,
        importable=False,
        exportable=True
    )

    obj_a = ModelAC.new(int_a=3)

    assert set(obj_a.to_dict().items()) >= set({
        "intA": 3
    }.items())

