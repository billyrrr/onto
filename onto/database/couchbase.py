from onto.common import _NA
from onto.database import Database, Reference, Snapshot
from onto.context import Context as CTX
from couchbase import bucket


class CouchbaseDatabase(Database):

    @classmethod
    def bucket(cls) -> bucket.Bucket:
        return CTX.dbs.couchbase

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.bucket().collection(collection_name=ref.first).upsert(
            key=ref.last, value=snapshot.to_dict()
        )

    @classmethod
    def create(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.bucket().collection(collection_name=ref.first).insert(
            key=ref.last, value=snapshot.to_dict()
        )

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        cls.bucket().collection(collection_name=ref.first).remove(
            key='ref.last'
        )

    @classmethod
    def update(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
        cls.set(ref, snapshot, transaction)
