from google.cloud.firestore import DocumentSnapshot, CollectionReference

from flask_boiler.firestore_object import snapshot_to_obj


def convert_query_ref(func):
    """ Converts a generator of firestore DocumentSnapshot's to a generator
        of objects

    :param super_cls:
    :return:
    """
    def call(cls, *args, **kwargs):
        query_ref = func(cls, *args, **kwargs)
        for res in query_ref.stream():
            assert isinstance(res, DocumentSnapshot)
            yield snapshot_to_obj(snapshot=res, super_cls=cls)
    return call


class QueryMixin:
    @classmethod
    def all(cls):
        """ Generator for all objects in the collection

        :return:
        """
        docs_ref: CollectionReference = cls._get_collection()
        docs = docs_ref.stream()
        for doc in docs:
            assert isinstance(doc, DocumentSnapshot)
            obj = cls.create(doc_id=doc.id)
            obj._import_properties(doc.to_dict())
            yield obj

    @classmethod
    @convert_query_ref
    def where(cls, *args, **kwargs):
        """ Note that indexes may need to be added from the link provided
                by firestore in the error messages

        TODO: add error handling and argument checking

        :param args:
        :param kwargs:
        :return:
        """

        if len(args) == 0 and len(kwargs) == 0:
            raise ValueError("Empty where")

        cur_where = cls._get_collection()

        if len(args) != 0:
            if len(args) % 3 != 0:
                raise ValueError
            else:
                arg_stack = list( args )

                while len(arg_stack) != 0:

                    cur_where = cur_where.where(
                        arg_stack.pop(0),
                        arg_stack.pop(0),
                        arg_stack.pop(0)
                    )

        for key, val in kwargs.items():
            cur_where = cur_where.where(key, "==", val)

        return cur_where
