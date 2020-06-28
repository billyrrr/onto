from flask_boiler.common import _NA
from flask_boiler.database import Database, Reference, Snapshot
from flask_boiler.context import Context as CTX
from couchbase import bucket


class CouchbaseDatabase(Database):

    @classmethod
    def bucket(cls) -> bucket.Bucket:
        return CTX.dbs.couchbase

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):

        if transaction is not _NA:
            raise ValueError

        # k = ref.first
        _id = ref.last

        coll = cls.bucket().collection('default')
        coll.upsert(_id, snapshot.to_dict())

