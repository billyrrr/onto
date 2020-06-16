from flask_boiler import schema, fields, domain_model, factory, attrs


class UserBase(domain_model.DomainModel):
    pass


class User(UserBase):

    class Meta:
        collection_name = "users"

    first_name = attrs.bproperty()
    last_name = attrs.bproperty()
    organization = attrs.bproperty()
    hearing_aid_requested = attrs.bproperty()
    display_name = attrs.bproperty(import_enabled=False)

    @display_name.getter
    def display_name(self):
        return "{} {}".format(self.first_name, self.last_name)
