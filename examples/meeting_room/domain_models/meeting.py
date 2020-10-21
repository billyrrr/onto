from onto import domain_model, attrs
# from . import Location, User, Ticket
from onto.collection_mixin import with_pony, db


class MeetingBase(domain_model.DomainModel, metaclass=with_pony):
    doc_ref = attrs.doc_ref(type_cls=str)

    class Meta:
        collection_name = "meetings"


class Meeting(MeetingBase):

    location = attrs.relation(nested=False, dm_cls='Location')
    users = attrs.relation(nested=False, dm_cls='User',
                           collection=list)
    tickets = attrs.relation(nested=False, dm_cls='Ticket',
                             collection=dict)
    status = attrs.bproperty(type_cls=str)
