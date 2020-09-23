from onto import schema, fields, domain_model, factory


class UserSchema(schema.Schema):
    followers = fields.Raw()


class UserBase(domain_model.DomainModel):

    class Meta:
        collection_name = "users"


class User(UserBase):

    class Meta:
        schema_cls = UserSchema
