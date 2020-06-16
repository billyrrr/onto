from flask_boiler import domain_model, schema, fields, factory, attrs
# from . import User

class TicketBase(domain_model.DomainModel):

    class Meta:
        collection_name = "tickets"


class Ticket(TicketBase):
    role = attrs.bproperty()
    user = attrs.relation(nested=False, dm_cls='User')
    attendance = attrs.bproperty()

