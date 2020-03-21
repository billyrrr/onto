from flask_boiler import schema, fields, domain_model, factory


class UserSchema(schema.Schema):

    first_name = fields.Str()
    last_name = fields.Raw()
    organization = fields.Raw()

    hearing_aid_requested = fields.Raw()


UserBase = factory.ClsFactory.create(
    name="UserBase",
    schema=UserSchema,
    base=domain_model.DomainModel
)


class User(UserBase):

    class Meta:
        collection_name = "users"

    @property
    def display_name(self):
        return "{} {}".format(self.first_name, self.last_name)

