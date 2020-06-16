from flask_boiler import fields, schema, domain_model
from .. import domain_models
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location
from marshmallow import fields as m_fields


def test_reference(users, tickets, location):
    """ Used as an experiment
    """

    from flask_boiler import attrs

    class ExpMeeting(domain_model.DomainModel):

        class Meta:
            collection_name = "meetings"

        location = attrs.relation(nested=False, dm_cls=domain_models.Location)
        users = attrs.relation(nested=False, dm_cls=domain_models.User, collection=list)
        tickets = attrs.relation(nested=False, dm_cls=domain_models.Ticket, collection=dict)
        status = attrs.bproperty()

    m = ExpMeeting.new(doc_id="meeting_1")
    m.users = [user.doc_ref for user in users]
    m.tickets = {ticket.user.id: ticket.doc_ref for ticket in tickets}
    m.location = location.doc_ref
    m.status = "in-session"

    assert m.to_dict() != dict()
