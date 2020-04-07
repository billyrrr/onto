from datetime import datetime
from flask_boiler import schema, fields, domain_model, utils
from flask_boiler.config import Config
from flask_boiler.serializable import BaseRegisteredModel, Schemed, Exportable, \
    NewMixin
from flask_boiler.context import Context as CTX

config = Config(
    app_name="flask-boiler-testing",
    debug=True,
    testing=True,
    certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
)

CTX.read(config)


# class Immutable(BaseRegisteredModel,
#                Schemed,
#                NewMixin,
#                Exportable,):
#     pass

class PostSchema(schema.Schema):
    _id = fields.Raw(data_key="id", dump_only=True)
    title = fields.Raw()
    body = fields.Raw()
    pub_date = fields.Raw()

    category = fields.Relationship(nested=True)


class PostBase(domain_model.DomainModel):

    @property
    def _id(self):
        return self.doc_id

    _collection_name = "posts"
    _schema_cls = PostSchema

    def __repr__(self):
        return '<Post %r>' % self.title


class Post(PostBase):
    pass


class CategorySchema(schema.Schema):
    _id = fields.Raw(data_key="id", dump_only=True)
    name = fields.Raw()
    # posts = fields.Relationship(nested=True, many=True)


class CategoryBase(domain_model.DomainModel):

    @property
    def _id(self):
        return self.doc_id

    _collection_name = "categories"
    _schema_cls = CategorySchema

    def __repr__(self):
        return '<Category %r>' % self.name


class Category(CategoryBase):
    pass


category_id = utils.random_id()
py = Category.new(doc_id=category_id)
py.name = "Python"

post_id = utils.random_id()
p = Post.new(doc_id=post_id)
p.title = "snakes"
p.body = "Ssssssss"

# py.posts.append(p)
p.category = py

py.save()

obj = Post.get(doc_id=post_id)

assert str(p.category) == "<Category 'Python'>"

assert p._export_as_view_dict() == {'body': 'Ssssssss',
                                    'id': post_id,
                                    'category': {
                                        'id': category_id,
                                        'name': 'Python'},
                                    'title': 'snakes',
                                    'pubDate': None}
