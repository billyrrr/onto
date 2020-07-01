from flask_boiler.common import _NA
from flask_boiler.database import Database, Reference, Snapshot
from flask_boiler.context import Context as CTX

from google.cloud import firestore


# TODO: NOTE maximum of 1 firestore client allowed since we used a global var.


class FirestoreReference(Reference):

    def is_collection(self):
        return len(self.params) % 2 == 1

    def is_document(self):
        return len(self.params) % 2 == 0

    def is_collection_group(self):
        return self.first == "**" and len(self.params) == 2


class FirestoreDatabase(Database):

    firestore_client = None

    @classmethod
    def transaction(cls):
        return cls.firestore_client.transaction()

    @classmethod
    def _doc_ref_from_ref(cls, ref):
        if ref._is_empty:
            # TODO: change this behavior
            return cls.firestore_client
        elif ref.is_collection_group():
            return cls.firestore_client.collection_group(ref.last)
        elif ref.is_collection():
            return cls.firestore_client.collection(str(ref))
        elif ref.is_document():
            return cls.firestore_client.document(str(ref))
        else:
            raise ValueError

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        doc_ref = cls._doc_ref_from_ref(ref)
        doc_ref.set(
            document_data=snapshot.to_dict()
        )

        if transaction is None:
            doc_ref.set(document_data=snapshot.to_dict())
        else:
            transaction.set(reference=doc_ref,
                            document_data=snapshot.to_dict())

    @classmethod
    def get(cls, ref: Reference, transaction=_NA):
        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        doc_ref = cls._doc_ref_from_ref(ref)

        if transaction is None:
            document_snapshot = doc_ref.get()
        else:
            document_snapshot = doc_ref.get(transaction=transaction)

        return FirestoreSnapshot.from_document_snapshot(
            document_snapshot=document_snapshot)

    @classmethod
    def update(cls, ref: Reference, snapshot: Snapshot):
        pass

    @classmethod
    def create(cls, ref: Reference, snapshot: Snapshot):
        pass

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        doc_ref = cls._doc_ref_from_ref(ref)
        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        if transaction is None:
            doc_ref.delete()
        else:
            transaction.delete(reference=doc_ref)

    ref = FirestoreReference()


class FirestoreSnapshot(Snapshot):

    @classmethod
    def from_document_snapshot(
            cls, document_snapshot: firestore.DocumentSnapshot):
        return cls(
            document_snapshot.to_dict()
        )
