from flask_boiler import domain_model, schema, fields, factory, attrs


class LocationBase(domain_model.DomainModel):

    class Meta:
        collection_name = "locations"

    latitude = attrs.bproperty()
    longitude = attrs.bproperty()
    address = attrs.bproperty()


class Location(LocationBase):

    pass
