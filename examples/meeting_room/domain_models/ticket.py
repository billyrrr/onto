from flask_boiler import domain_model, schema, fields, factory


class TicketSchema(schema.Schema):

    role = fields.Raw()
    user = fields.Relationship(nested=False)
    attendance = fields.Boolean()


class TicketBase(domain_model.DomainModel):

    class Meta:
        collection_name = "tickets"


class Ticket(TicketBase):

    class Meta:
        schema_cls = TicketSchema

