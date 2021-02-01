from onto import domain_model
from onto.attrs import attrs
# from onto.collection_mixin import with_pony


class UserBase(domain_model.DomainModel
    # , metaclass=with_pony
               ):
    # doc_ref = attrs.doc_ref(type_cls=str)
    pass


class User(UserBase):

    class Meta:
        collection_name = "users"

    first_name = attrs.str
    last_name = attrs.str
    organization = attrs.str
    hearing_aid_requested = attrs.str
    display_name = attrs.str.optional

    meetings = attrs.list(
        value=lambda a: a.relation('Meeting')
    ).optional.default_value(list)
    tickets = attrs.list(
        value=lambda a: a.relation('Tickets')
    ).optional.default_value(list)


    @classmethod
    def _datastore(cls):
        from onto.database.mock import MockDatabase
        return MockDatabase

    @display_name.getter
    def display_name(self):
        return "{} {}".format(self.first_name, self.last_name)
