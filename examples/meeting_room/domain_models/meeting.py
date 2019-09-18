from flask_boiler import domain_model, schema, fields, factory


class MeetingSchema(schema.Schema):

    location = fields.Relationship(nested=False)
    users = fields.Relationship(nested=False, many=True)
    tickets = fields.Relationship(nested=False, many=True)

    status = fields.Raw()


class MeetingBase(domain_model.DomainModel):

    _collection_name = "meetings"


Meeting = factory.ClsFactory.create(
    "Meeting", MeetingSchema, base=MeetingBase)



