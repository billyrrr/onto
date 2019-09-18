from flask_boiler import domain_model, schema, fields, factory


class TicketSchema(schema.Schema):

    role = fields.Raw()
    user = fields.Relationship(nested=False)
    attendance = fields.Boolean()


class TicketBase(domain_model.DomainModel):

    _collection_name = "tickets"


Ticket = factory.ClsFactory.create(
    "Ticket", TicketSchema, base=TicketBase)


