from onto import schema, fields, domain_model, factory


class PostSchema(schema.Schema):
    owner_id = fields.Str()


class PostBase(domain_model.DomainModel):

    class Meta:
        collection_name = "insta_posts"


class Post(PostBase):

    class Meta:
        schema_cls = PostSchema
