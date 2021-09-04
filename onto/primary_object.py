import warnings

# from google.cloud.firestore_v1 import Transaction

from onto.collection_mixin import CollectionMixin, CollectionMemberMeta
from onto.firestore_object import FirestoreObject
from onto.query.query_mixin import QueryMixin
from onto.models.meta import SerializableMeta
from onto.utils import random_id, doc_ref_from_str

from onto.mapper import schema, fields


class PrimaryObjectSchema(schema.Schema):

    doc_id = fields.DocIdField(
        attribute="doc_id",
        dump_only=True,
        data_key="doc_id",
        required=False
    )

    doc_ref = fields.DocRefField(
        attribute="doc_ref",
        dump_only=True,
        data_key="doc_ref",
        required=False
    )


def _collect_query_schema(klass):
    d = dict(klass.get_schema_obj().fields)
    for child in klass._get_children():
        for key, val in child.get_schema_obj().fields.items():
            field_obj = val

            if key in d and d[key] != field_obj:
                warnings.warn(
                    f"Conflict when resolving field for {key}. The "
                    f"field is for querying database "
                    f"from a parent PrimaryObject when "
                    f"such base has no declared schema. ")
            else:
                d[key] = field_obj
    tmp_schema = klass._schema_base.from_dict(d)
    return tmp_schema


class PrimaryObject(FirestoreObject, QueryMixin, CollectionMixin,
                    metaclass=CollectionMemberMeta):
    """
    Primary Object is placed in a collection in root directory only.
    the document will be stored in and accessed from
            self.collection.document(doc_id)

    """

    _collection_name = None
    _schema_base = PrimaryObjectSchema

    @classmethod
    def _query_schema(cls):
        return _collect_query_schema(cls)()

    # @classmethod
    # def get_schema_cls(cls):
    #     """ Returns schema_cls or the union of all schemas of subclasses.
    #             Should only be used on the root DomainModel. Does not
    #             cache the result.
    #
    #     """
    #     d = dict()
    #     if super().get_schema_cls() is None:
    #         for child in cls._get_children():
    #             for key, val in child.get_schema_obj().fields.items():
    #                 field_obj = val
    #
    #                 if key in d and d[key] != field_obj:
    #                     warnings.warn(
    #                         f"Conflict when resolving field for {key}. The "
    #                         f"field is for querying database "
    #                         f"from a parent PrimaryObject when "
    #                         f"such base has no declared schema. ")
    #                 else:
    #                     d[key] = field_obj
    #         tmp_schema = cls._schema_base.from_dict(d)
    #         return tmp_schema
    #     else:
    #         return super().get_schema_cls()

    @property
    def doc_id(self):
        """ Returns Document ID
        """
        return self.doc_ref.id
    #
    # @property
    # def doc_ref(self):
    #     """ Returns Document Reference
    #     """
    #     return self._doc_ref

    random_id = random_id

    @classmethod
    def new(cls, doc_id=None, doc_ref=None, **kwargs):
        """ Creates an instance of object and assign a firestore reference
        with random id to the instance. This is similar to the use
        of "new" in Java. It is recommended that you use "new" to
        initialize an object, rather than the native initializer.
        Values are initialized based on the order that they are
        declared in the schema.

        :param: doc_id: Document ID
        :param: doc_ref: Document Reference
        :param allow_default: if set to False, an error will be
            raised if value is not provided for a field.
        :param kwargs: keyword arguments to pass to the class
            initializer.
        :return: the instance created
        """
        if doc_ref is None:
            if doc_id is None:
                doc_id = cls.random_id()
            doc_ref = cls.ref_from_id(doc_id=doc_id)
        obj = super().new(doc_ref=doc_ref, **kwargs)
        return obj

    @classmethod
    def get(cls, *, doc_ref_str=None, doc_ref=None, doc_id=None,
            transaction: 'google.cloud.firestore_v1.Transaction'=None):
        """ Returns the instance from doc_id.

        :param doc_ref_str: DocumentReference path string
        :param doc_ref: DocumentReference
        :param doc_id: gets the instance from self.collection.document(doc_id)
        :param transaction: firestore transaction
        """

        if doc_ref_str is not None:
            doc_ref = doc_ref_from_str(doc_ref_str)

        if doc_ref is None:
            doc_ref = cls.ref_from_id(doc_id=doc_id)

        return super().get(doc_ref=doc_ref, transaction=transaction)
