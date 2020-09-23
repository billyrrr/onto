from google.cloud.firestore_v1 import Query

from examples.fluttergram.domain_models import Post, User
from onto.store.business_property_store import BPSchema
from onto.store.struct import Struct

from onto.view import ViewMediatorDeltaDAV
from onto import utils, schema, fields, testing_utils
from onto import view_model
# Import the fixtures used by fixtures


class PostDAVSchema(schema.Schema):
    post = fields.Embedded(dump_only=True)


class PostStoreBpss(BPSchema):
    consumer = fields.StructuralRef(dm_cls=User)
    post = fields.StructuralRef(dm_cls=Post)


class PostDAV(view_model.ViewModel):
    class Meta:
        schema_cls = PostDAVSchema

    @property
    def post(self):
        return self.store.post

    @classmethod
    def new(cls, *args, consumer_id, post_id, **kwargs):
        ref = User._get_collection().document(consumer_id).collection("feed") \
            .document(post_id)

        struct = Struct(schema_obj=PostStoreBpss())
        struct["consumer"] = (User, consumer_id)
        struct["post"] = (Post, post_id)

        obj = cls.get(*args, struct_d=struct, doc_ref=ref, **kwargs)

        return obj


class FeedEntryViewMediatorDeltaDAV(ViewMediatorDeltaDAV):

    def __init__(self, *args, post_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_cls = post_cls

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.post_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':
                    post = utils.snapshot_to_obj(
                        snapshot,
                        super_cls=self.post_cls
                    )

                    producer_id = post.owner_id
                    producer = User.get(doc_id=producer_id)
                    followers = list()
                    for key, val in producer.followers.items():
                        if val is True:
                            followers.append(key)

                    for consumer_id in followers:
                        obj = self.view_model_cls.new(
                            consumer_id=consumer_id,
                            post_id=post.doc_id,
                            once=False,
                            f_notify=self.notify
                        )

        return query, on_snapshot


def test_start(users, posts):
    mediator = FeedEntryViewMediatorDeltaDAV(
        view_model_cls=PostDAV,
        post_cls=Post,
    )

    mediator.start()

    testing_utils._wait(factor=.2)

    ref = User._get_collection().document("thomasina").collection("feed") \
        .document(posts[0].doc_id)

    assert ref.get().to_dict() == {'obj_type': 'PostDAV',
                                   'post': {'ownerId': 'tijuana',
                                            'doc_ref': 'insta_posts/tj_t',
                                            'obj_type': 'Post',
                                            'hello': 'world',
                                            'doc_id': 'tj_t'},
                                   'doc_ref': 'users/thomasina/feed/tj_t'}
