from onto.context import Context as CTX
# from google.cloud.firestore import CollectionReference

from onto.database import Reference
from onto.firestore_object import FirestoreObject
from onto.models.meta import SerializableMeta


class CollectionMemberMeta(SerializableMeta):

    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)
        if hasattr(klass, "Meta"):
            meta = klass.Meta
            if hasattr(meta, "collection_name"):
                klass._collection_name = meta.collection_name
        return klass


try:
    from pony.orm.core import EntityMeta
    class with_pony(EntityMeta, CollectionMemberMeta):

        def __new__(mcs, name, bases, attrs):
            db = CTX.dbs.pony
            bases = (*bases, db.Entity,)
            klass = super().__new__(mcs, name, bases, attrs)
            return klass

        def __init__(mcs, name, bases, attrs):
            db = CTX.dbs.pony
            bases = (*bases, db.Entity,)
            super().__init__(name, bases, attrs)
except ImportError:
    import warnings
    warnings.warn("with_pony skipped")


class CollectionMixin:

    _collection_name = None

    @property
    def collection_name(self):
        """ Returns the root collection name of the class of objects.
                If cls._collection_name is not specified, then the collection
                name will be inferred from the class name. Note that different
                types of objects may share one collection.
        """
        # if type(self) == FirestoreObject:
        #     raise ValueError("collection_name is read from class name, "
        #                      "only subclass is supported. ")
        return self._get_collection_name()

    @classmethod
    def _get_collection_name(cls):
        if cls._collection_name is None:
            cls._collection_name = cls.__name__
        return cls._collection_name

    @property
    def collection(self):
        """ Returns the firestore collection of the current object
        """
        return self._get_collection()

    @classmethod
    def _get_collection(cls) -> Reference:
        return cls._datastore().ref / cls._get_collection_name()

    @classmethod
    def ref_from_id(cls, doc_id):
        """ Returns a Document Reference from doc_id supplied.

        :param doc_id: Document ID
        """
        return cls._get_collection() / doc_id
