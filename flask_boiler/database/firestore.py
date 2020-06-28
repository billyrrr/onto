from flask_boiler.common import _NA
from flask_boiler.database import Database, Reference, Snapshot
from flask_boiler.context import Context as CTX

from google.cloud import firestore


class FirestoreDatabase(Database):

    @classmethod
    def _doc_ref_from_ref(cls, ref):
        return CTX.db.document(ref)

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


class FirestoreSnapshot(Snapshot):

    @classmethod
    def from_document_snapshot(
            cls, document_snapshot: firestore.DocumentSnapshot):
        return cls(
            document_snapshot.to_dict()
        )
