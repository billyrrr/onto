from onto import domain_model, attrs
# from . import User
# from onto.collection_mixin import with_pony


class TicketBase(domain_model.DomainModel,
                 # metaclass=with_pony
                 ):
    doc_ref = attrs.doc_ref(type_cls=str)

    class Meta:
        collection_name = "tickets"


class Ticket(TicketBase):

    @classmethod
    def _datastore(cls):
        from onto.database.kafka import KafkaDatabase
        return KafkaDatabase

    role = attrs.bproperty(type_cls=str)
    user = attrs.relation(nested=False, dm_cls='User')
    attendance = attrs.bproperty(type_cls=bool)

    meetings = attrs.relation(import_required=False, dm_cls='Meeting', collection=list, nested=False)

