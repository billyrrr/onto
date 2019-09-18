from flask_boiler import domain_model, schema, fields, factory


class LocationSchema(schema.Schema):

    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()


class LocationBase(domain_model.DomainModel):

    _collection_name = "locations"


Location = factory.ClsFactory.create(
    "Location", LocationSchema, base=LocationBase)
