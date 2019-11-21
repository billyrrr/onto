from flask_boiler import domain_model, schema, fields, factory


class MeetingSchema(schema.Schema):

    location = fields.Relationship(nested=False)
    users = fields.Relationship(nested=False, many=True)
    tickets = fields.Relationship(nested=False, many=True)

    status = fields.Raw()


class MeetingBase(domain_model.DomainModel):

    class Meta:
        collection_name = "meetings"


class Meeting(MeetingBase):

    class Meta:
        schema_cls = MeetingSchema
