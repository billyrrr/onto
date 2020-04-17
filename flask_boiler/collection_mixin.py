from flask_boiler.context import Context as CTX
from google.cloud.firestore import CollectionReference


class CollectionMixin:

    # _collection_name = None

    @classmethod
    def _doc_ref_from_id(cls, doc_id):
        return cls._get_collection().document(doc_id)

    @property
    def collection_name(self):
        """ Returns the root collection name of the class of objects.
                If cls._collection_name is not specified, then the collection
                name will be inferred from the class name.

        :return:
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

        :return:
        """
        return self._get_collection()

    @classmethod
    def _get_collection(cls) -> CollectionReference:
        return CTX.db.collection(cls._get_collection_name())

    @classmethod
    def ref_from_id(cls, doc_id):
        """ Returns a Document Reference from doc_id supplied.

        :param doc_id: Document ID
        :return:
        """
        return cls._get_collection().document(document_id=doc_id)
