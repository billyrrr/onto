from google.cloud.firestore_v1 import Transaction

from flask_boiler.firestore_object import FirestoreObject


class ReferencedObject(FirestoreObject):
    """
    ReferencedObject may be placed anywhere in the database.
    """

    @property
    def doc_ref(self):
        return self._doc_ref

    @classmethod
    def get(cls, *, doc_ref=None, transaction: Transaction = None, **kwargs):
        """ Returns an instance from firestore document reference.

        :param doc_ref: firestore document reference
        :param transaction: firestore transaction
        :return:
        """
        return super().get(doc_ref=doc_ref, transaction=transaction)
