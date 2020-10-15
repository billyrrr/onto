from onto import domain_model, attrs
from onto.collection_mixin import with_pony


class UserBase(domain_model.DomainModel, metaclass=with_pony):
    doc_ref = attrs.doc_ref(type_cls=str)


class User(UserBase):

    class Meta:
        collection_name = "users"

    first_name = attrs.bproperty(type_cls=str)
    last_name = attrs.bproperty(type_cls=str)
    organization = attrs.bproperty(type_cls=str)
    hearing_aid_requested = attrs.bproperty(type_cls=bool)
    display_name = attrs.bproperty(type_cls=str, import_enabled=False)

    meetings = attrs.relation(import_required=False, dm_cls='Meeting', collection=list, nested=False)
    tickets = attrs.relation(import_required=False, dm_cls='Ticket', collection=list, nested=False)


    @display_name.getter
    def display_name(self):
        return "{} {}".format(self.first_name, self.last_name)
