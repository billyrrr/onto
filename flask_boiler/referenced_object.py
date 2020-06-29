from google.cloud.firestore_v1 import Transaction

from flask_boiler.models.base import Serializable
from flask_boiler import schema, fields


class ReferencedObjectSchema(schema.Schema):

    doc_ref = fields.String(
        # attribute="doc_ref",
        # # dump_only=True,
        # data_key="doc_ref",
        required=False,
        allow_none=True
    )


class ReferencedObject(Serializable):
    """
    ReferencedObject may be placed anywhere in the database.
    """
    _schema_base = ReferencedObjectSchema

    #
    # @property
    # def doc_ref(self):
    #     return self._doc_ref

    # @classmethod
    # def get(cls, *, doc_ref=None, transaction: Transaction = None, **kwargs):
    #     """ Returns an instance from firestore document reference.
    #
    #     :param doc_ref: firestore document reference
    #     :param transaction: firestore transaction
    #     :return:
    #     """
    #     return super().get(doc_ref=doc_ref, transaction=transaction)
