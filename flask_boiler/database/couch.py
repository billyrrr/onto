from flask_boiler.common import _NA
from flask_boiler.database import Database, Reference, Snapshot
from flask_boiler.context import Context as CTX

class CouchDatabase(Database):
    import couchdb

    @classmethod
    def server(cls) -> couchdb.Server:
        return CTX.dbs.couch

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):

        if transaction is not _NA:
            raise ValueError

        k = ref.first
        _id = ref.last

        db = cls.server()[k]
        db.save({
            '_id': _id,
            **snapshot
        })
