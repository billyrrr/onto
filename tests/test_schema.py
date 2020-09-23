from unittest import mock, skip

import pytest
from testfixtures import compare

import onto.utils
from onto import schema, fields
from onto.errors import PropertyEvalError
from onto.mapper.schema import Schema, BoilerProperty
from onto.models.base import Serializable


def test__get_instance_vars():
    class TestObject:

        def __init__(self):
            self.int_a = 0
            self.int_b = 0

    obj_cls = TestObject

    res = schema._get_instance_variables(obj_cls)

    assert res == ["int_a", "int_b"]


@pytest.mark.skip
def test__get_instance_vars_nested_init():
    class TestObject:

        def _nested_init(self):
            self.int_c = 0

        def __init__(self):
            self.int_a = 0
            self.int_b = 0
            self._nested_init()

    obj_cls = TestObject

    res = schema._get_instance_variables(obj_cls)
    # print(res)
    assert res == ["int_a", "int_b", "int_c"]


@pytest.mark.skip
def test__get_field_vars():
    """
    Tests that _get_field_vars returns a dictionary of expected Field objects.
    """

    # class TestObject:
    #
    #     def __init__(self):
    #         self.int_a = 0
    #         self.int_b = 0

    # obj_cls = TestObject

    field_vars = schema._get_field_vars(["int_a", "int_b"],
                                        fd=["int_a", "int_b"])

    def field_comparator(x, y, _):
        """
        Test fixture for comparing two fields.Field objects
        """
        if x.load_from != y.load_from:
            return "x != y since x.load_from: {} != y.load_from: {}".format(
                x.load_from, y.load_from
            )

    compare(

        field_vars, {
            "int_a": fields.Raw(load_from="intA"),
            "int_b": fields.Raw(load_from="intB"),
        }, comparers={fields.Field: field_comparator}

    )


def test_set_attr():
    """
    Tests that generate_schema returns a schema that has the ability to
        set instance variables based on keys of different format in the
        dictionary provided in schema.load(d)
    """

    class TestObject(object):

        def __init__(self):
            super().__init__()
            self.int_a = 0
            self.int_b = 0

        @classmethod
        def get_fields(cls):
            return ["int_a", "int_b"]

        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls, *args, **kwargs)
            return instance

    s = schema.generate_schema(TestObject)

    # print(s)

    obj = s.load({
        "intA": 1,
        "intB": 2
    })

    assert obj.int_a == 1
    assert obj.int_b == 2

    # TODO: test that no extraneous attributes are set


def test_conversion():
    """
    Tests that "camelCase" key used in Firestore converts to "snake_case"
        target instance variable names.
    """

    res = onto.utils.firestore_key_to_attr_name("intA")
    assert res == "int_a"

    r_res = onto.utils.attr_name_to_firestore_key("int_a")
    assert r_res == "intA"


@pytest.fixture
def location_schema_fields():

    coordinates_field = fields.Raw()
    coordinates_field.deserialize = mock.MagicMock()
    address_field = fields.Raw()
    address_field.deserialize = mock.MagicMock()

    class LocationSchema(schema.Schema):
        coordinates = coordinates_field
        address = address_field

    return LocationSchema(), coordinates_field, address_field


def test_raw():
    coordinates_field = fields.Raw()
    address_field = fields.Raw()

    class LocationSchema(schema.Schema):
        coordinates = coordinates_field
        address = address_field

    location_schema = LocationSchema()

    serialized = {
        "coordinates": {
            "latitude": 36.98765,
            "longitude": 100.12345,
        },

        "address": "9500 Gilman Dr."
    }

    mres = location_schema.load(serialized)

    deserialized_dict = mres

    assert deserialized_dict == serialized


def test_schema_new():
    from onto.primary_object import PrimaryObjectSchema
    class CitySchema(PrimaryObjectSchema):
        city_name = fields.Raw(data_key="name")

        country = fields.Raw(data_key="country")
        capital = fields.Raw(data_key="capital")

    class MunicipalitySchema(CitySchema):
        pass

    class StandardCitySchema(CitySchema):
        city_state = fields.Raw(data_key="state")
        regions = fields.Raw(many=True, data_key="regions")

    assert set(CitySchema().fields.keys()) == {
        "city_name", "country", "capital",
        "doc_id", "doc_ref", "obj_type", "_remainder"
    }

    assert set(MunicipalitySchema().fields.keys()) == {
        "city_name", "country", "capital",
        "doc_id", "doc_ref", "obj_type", "_remainder"
    }

    assert set(StandardCitySchema().fields.keys()) == {
        "city_state", "regions",
        "city_name", "country", "capital",
        "doc_id", "doc_ref", "obj_type", "_remainder"
    }


def test_schema_dump():

    class CitySchema(Schema):
        city_name = fields.Raw()

        country = fields.Raw()
        capital = fields.Raw()

    class MunicipalitySchema(CitySchema):
        pass

    class StandardCitySchema(CitySchema):
        city_state = fields.Raw()
        regions = fields.Raw(many=True)

    assert MunicipalitySchema().dump({
        'city_name': 'Washington D.C.',
        'country': 'USA',
        'capital': True,
        # 'obj_type': "Municipality",
        # 'doc_id': 'DC',
        # 'doc_ref': 'City/DC'
    }) == {
        'cityName': 'Washington D.C.',
        'country': 'USA',
        'capital': True,
        'obj_type': "dict",
        # 'doc_id': 'DC',
        # 'doc_ref': 'City/DC'
    }


def test_schema_load():

    class CitySchema(Schema):
        city_name = fields.Raw()

        country = fields.Raw()
        capital = fields.Raw()

    class MunicipalitySchema(CitySchema):
        pass

    class StandardCitySchema(CitySchema):
        city_state = fields.Raw()
        regions = fields.Raw(many=True)

    assert MunicipalitySchema().load({
        'cityName': 'Washington D.C.',
        'country': 'USA',
        'capital': True,
    }) == {
        'city_name': 'Washington D.C.',
        'country': 'USA',
        'capital': True,
    }


def test_property_get_error_handling():

    class CitySchemaExtended(Schema):
        city_name = fields.Raw()

        country = fields.Raw()
        capital = fields.Raw()

        extra_property = fields.Raw(dump_only=True)

    class CityExtra(Serializable):

        _schema_cls = CitySchemaExtended

        @BoilerProperty
        def extra_property(self):
            return self.non_existent_property

    city = CityExtra.new(city_name="San Diego", country="USA", capital=False)

    """
    Tests that AttributeError is not swallowed when 
        the property function is located but failed 
        during evaluation 
    """
    with pytest.raises(PropertyEvalError) as excinfo:
        res = CitySchemaExtended().dump(city)

    assert isinstance(excinfo.value.__cause__, AttributeError)

    """
    Tests that AttributeError is raised when accessing 
        a property that does not exist 
    TODO: move to test_serializable 
    """
    with pytest.raises(AttributeError):
        city.non_existent_property
