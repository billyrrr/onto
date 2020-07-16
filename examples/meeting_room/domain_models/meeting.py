from flask_boiler import domain_model, schema, fields, factory, attrs
# from . import Location, User, Ticket


class MeetingBase(domain_model.DomainModel):

    class Meta:
        collection_name = "meetings"


class Meeting(MeetingBase):

    location = attrs.relation(nested=False, dm_cls='Location')
    users = attrs.relation(nested=False, dm_cls='User',
                           collection=list)
    tickets = attrs.relation(nested=False, dm_cls='Ticket',
                             collection=dict)
    status = attrs.bproperty()
