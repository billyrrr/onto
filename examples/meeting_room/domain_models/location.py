from flask_boiler import domain_model, schema, fields, factory


class LocationSchema(schema.Schema):

    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()


class LocationBase(domain_model.DomainModel):
    class Meta:
        collection_name = "locations"


class Location(LocationBase):

    class Meta:
        schema_cls = LocationSchema
