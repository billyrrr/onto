from flask_boiler.context import Context as CTX
from google.cloud.firestore import CollectionReference

from flask_boiler.database import Reference
from flask_boiler.models.meta import SerializableMeta


class CollectionMemberMeta(SerializableMeta):

    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)
        if hasattr(klass, "Meta"):
            meta = klass.Meta
            if hasattr(meta, "collection_name"):
                klass._collection_name = meta.collection_name
        return klass



class CollectionMixin:

    # _collection_name = None

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
