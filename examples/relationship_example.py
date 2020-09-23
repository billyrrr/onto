from datetime import datetime
from onto import schema, fields, domain_model, utils, attrs
from onto.config import Config
from onto.models.mixin import Exportable, NewMixin
from onto.models.base import BaseRegisteredModel, Schemed
from onto.context import Context as CTX


if not CTX._ready:
    config = Config(
        app_name="flask-boiler-testing",
        debug=True,
        testing=True,
        certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
    )

    CTX.read(config)

class Post(domain_model.DomainModel):

    _collection_name = "posts"

    _id = attrs.bproperty(data_key="id", import_enabled=False)

    @_id.getter
    def _id(self):
        return self.doc_id

    title = attrs.bproperty()
    body = attrs.bproperty()
    pub_date = attrs.bproperty(export_default=None)

    category = attrs.relation(dm_cls='Category', nested=True)

    def __repr__(self):
        return '<Post %r>' % self.title


class Category(domain_model.DomainModel):
    _id = attrs.bproperty(data_key="id", import_enabled=False)

    name = attrs.bproperty()
    posts = attrs.relation(dm_cls='Post', nested=True, collection=list)

    @_id.getter
    def _id(self):
        return self.doc_id

    _collection_name = "categories"

    def __repr__(self):
        return '<Category %r>' % self.name


category_id = utils.random_id()
py = Category.new(doc_id=category_id)
py.name = "Python"

post_id = utils.random_id()
p = Post.new(doc_id=post_id)
p.title = "snakes"
p.body = "Ssssssss"

# py.posts.append(p)
p.category = py

py.posts.append(p)

p.save()

obj = Post.get(doc_id=post_id)

assert str(obj.category) == "<Category 'Python'>"

print(obj)

# assert obj._export_as_view_dict() == {'body': 'Ssssssss',
#                                     'id': post_id,
#                                     'category': {
#                                         'id': category_id,
#                                         'name': 'Python'},
#                                     'title': 'snakes',
#                                     'pubDate': None}

assert p.category.doc_id == category_id
