from onto import fields, schema, domain_model
from .. import domain_models
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location
from marshmallow import fields as m_fields


def test_reference(users, tickets, location):
    """ Used as an experiment
    """

    from onto import attrs

    class ExpMeeting(domain_model.DomainModel):

        class Meta:
            collection_name = "meetings"

        location = attrs.relation(nested=True, dm_cls=domain_models.Location)
        users = attrs.relation(nested=True, dm_cls=domain_models.User, collection=list)
        tickets = attrs.relation(nested=True, dm_cls=domain_models.Ticket, collection=dict)
        status = attrs.bproperty()

    m = ExpMeeting.new(doc_id="meeting_1")
    m.users = [user for user in users]
    m.tickets = {ticket.user.id: ticket for ticket in tickets}
    m.location = location
    m.status = "in-session"

    md = m.to_dict()

    mo = ExpMeeting.from_dict(d=md)
    u = mo.users[0]
    assert u is not None
