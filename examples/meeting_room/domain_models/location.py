from onto import domain_model, attrs
# from onto.collection_mixin import with_pony


class LocationBase(domain_model.DomainModel
    # , metaclass=with_pony
                   ):
    # doc_ref = attrs.doc_ref(type_cls=str)

    class Meta:
        collection_name = "locations"



class Location(LocationBase):

    @classmethod
    def _datastore(cls):
        from onto.database.kafka import KafkaDatabase
        return KafkaDatabase

    latitude = attrs.bproperty(type_cls=float)
    longitude = attrs.bproperty(type_cls=float)
    address = attrs.bproperty(type_cls=float)
    meetings = attrs.relation(dm_cls='Meeting', import_required=False, collection=list, nested=False)
