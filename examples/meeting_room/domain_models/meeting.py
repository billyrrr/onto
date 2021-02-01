from onto import domain_model, attrs
# from . import Location, User, Ticket
# from onto.collection_mixin import with_pony, db


class MeetingBase(domain_model.DomainModel
    # , metaclass=with_pony
                  ):
    doc_ref = attrs.doc_ref(type_cls=str)

    class Meta:
        collection_name = "meetings"

    location = attrs.relation(nested=False, dm_cls='Location')
    users = attrs.relation(nested=False, dm_cls='User',
                           collection=list)
    tickets = attrs.relation(nested=False, dm_cls='Ticket',
                             collection=list)
    status = attrs.bproperty(type_cls=str)


class Meeting(MeetingBase,
              # metaclass=with_pony
              ):

    @classmethod
    def _datastore(cls):
        from onto.database.kafka import KafkaDatabase
        return KafkaDatabase


# class MeetingIn(MeetingBase):
#
#     @classmethod
#     def _datastore(cls):
#         from onto.database.kafka import KafkaDatabase
#         return KafkaDatabase
