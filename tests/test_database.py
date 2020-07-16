from flask_boiler.database.firestore import TargetIdAssigner
from flask_boiler.query.query import DomainModelQuery


def test_reference():

    from flask_boiler.database import Reference

    r = Reference()
    a = r.child('a')
    ab = a.child('b')
    assert a == 'a'
    assert ab == 'a/b'


def test_reference_truediv():

    from flask_boiler.database import Reference

    r = Reference()
    a = r / 'a'
    ab = a / 'b'
    assert a == 'a'
    assert ab == 'a/b'

    assert a/'c'/'d' == 'a/c/d'
    assert a/'e'/'f'/'g' == 'a/e/f/g'


def test_reference_truediv_eq():
    """ Tests that "/=" creates a new Reference object
    """

    from flask_boiler.database import Reference

    r = Reference()
    r /= 'a'
    pre = id(r)
    assert r == 'a'
    r /= 'b'
    post = id(r)
    assert r == 'a/b'

    assert pre != post


def test_deserialize():

    from flask_boiler.database import Reference

    r = Reference.from_str(s='a/b')

    assert r == 'a/b'
    assert isinstance(r, Reference)
    assert not r._is_empty

    r = Reference.from_str(s='')
    assert r == ''
    assert isinstance(r, Reference)
    assert r._is_empty

    # This behavior is arbitrary and may be changed
    r = Reference.from_str(s='/')
    assert r == '/'
    assert isinstance(r, Reference)
    assert not r._is_empty


def test_serialize():

    from flask_boiler.database import Reference

    r = Reference()
    a = r.child('a')
    ab = a.child('b')
    assert str(a) == 'a'
    assert str(ab) == 'a/b'


def test_leancloud():
    from flask_boiler.database.leancloud import LeancloudDatabase
    from flask_boiler.database import Snapshot

    ref = LeancloudDatabase.ref/'TODO'/'582570f38ac247004f39c24b'
    snapshot = Snapshot(title='foo', priority='bar')
    LeancloudDatabase.set(ref=ref, snapshot=snapshot)


def test_target_id_assigner():
    assigner = TargetIdAssigner()
    assert assigner.assign_id() == 32
    assert assigner.assign_id() == 33
    assigner.release_id(32)
    assert assigner.assign_id() == 32
    assert assigner.assign_id() == 34
    assert assigner.assign_id() == 35


def test_watch():
    from flask_boiler.watch import _Watch
    from flask_boiler.context import Context as CTX
    from google.cloud import firestore

    def callback(*args, **kwargs):
        print(f"{args} {kwargs}")

    _watch = _Watch(
        firestore=CTX.db.firestore_client,
        comparator=lambda d1, d2: 1,
        # snapshot_callback=callback,
        document_snapshot_cls=firestore.DocumentSnapshot,
        document_reference_cls=firestore.DocumentReference,
    )

    from google.cloud import firestore
    t1_ref = CTX.db.firestore_client.document('s/t1')
    t2_ref = CTX.db.firestore_client.document('s/t2')
    t1_ref.set({'foo': 'bar'})
    t2_ref.set({'foo': 'bar'})
    document_refs = [t1_ref._document_path, t2_ref._document_path]

    target = {
        "documents": {"documents": document_refs},
        "target_id": 0x2,
        "once": False
    }

    _watch.add_target(target, callback)

    from flask_boiler import testing_utils

    testing_utils._wait()
    # TODO: add and test tearDown for _watch
    # Implement close() for listener

def test_listener():
    from flask_boiler.database.firestore import FirestoreListener, Query
    from flask_boiler.domain_model import DomainModel
    from flask_boiler import attrs

    class S(DomainModel):

        foo = attrs.bproperty()
        obj_type = attrs.object_type(import_enabled=False, export_enabled=False)

        class Meta:
            collection_name = 'S'

    S.new(doc_id='T', foo='bar').save()

    query = DomainModelQuery(parent=S, arguments=[])

    from flask_boiler.source.firestore import FirestoreSource
    class M:
        source = FirestoreSource(query=query)

        @staticmethod
        @source.triggers.on_create
        def add_t(ref, snapshot):
            print(f"{ref} {snapshot}")

        @classmethod
        def start(cls):
            cls.source.start()

    M.start()

    from flask_boiler import testing_utils
    testing_utils._wait()

    testing_utils._wait()


def test_snapshot_init_meta():
    from flask_boiler.database.firestore import FirestoreSnapshot
    snapshot = FirestoreSnapshot.from_data_and_meta(
        data=dict(foo='bar'),
        my_arg=1
    )
    assert snapshot['foo'] == 'bar'
    assert 'my_arg' not in snapshot
    assert snapshot.my_arg == 1


# def test_stuffs():
#
#     from collections import UserDict
#
#     class ExpD(UserDict):
#         def __getitem__(self, item):
#             print(item)
#
#     ExpD()[1:2]
