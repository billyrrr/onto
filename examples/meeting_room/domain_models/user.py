from flask_boiler import schema, fields, domain_model, factory


class UserSchema(schema.Schema):

    first_name = fields.Raw()
    last_name = fields.Raw()
    organization = fields.Raw()

    hearing_aid_requested = fields.Raw()


class UserBase(domain_model.DomainModel):

    _collection_name = "users"

    @property
    def display_name(self):
        return "{} {}".format(self.first_name, self.last_name)


User = factory.ClsFactory.create(
    "User", UserSchema, base=UserBase)

