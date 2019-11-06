from google.cloud.firestore import DocumentSnapshot, CollectionReference, Query

from flask_boiler.utils import snapshot_to_obj


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

            yield snapshot_to_obj(snapshot=doc, super_cls=cls)

    @staticmethod
    def _append_original(*args, cur_where=None) -> Query:
        if cur_where is None:
            raise ValueError

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
        return cur_where

    @classmethod
    def _append_new_style(cls, *, cur_where=None, **kwargs):
        if cur_where is None:
            raise ValueError

        for key, val in kwargs.items():
            comp, other = val if isinstance(val, tuple) else ("==", val)
            firestore_key = cls.get_schema_cls().f(key)
            cur_where = cur_where.where(firestore_key, comp, other)
        return cur_where

    @classmethod
    def _where_query(cls, *args, cur_where=None, **kwargs):
        # if len(args) == 0 and len(kwargs) == 0:
        #     raise ValueError("Empty where")
        if cur_where is None:
            raise ValueError

        cur_where = cls._append_original(*args, cur_where=cur_where)
        cur_where = cls._append_new_style(**kwargs, cur_where=cur_where)
        return cur_where

    @classmethod
    @convert_query_ref
    def where(cls, *args,
              acsending=None,
              descending=None,
              end_at=None,
              end_before=None,
              limit=None,
              offset=None,
              order_by=None,
              select=None,
              start_after=None,
              start_at=None,
              **kwargs,):
        """ Note that indexes may need to be added from the link provided
                by firestore in the error messages

        TODO: add error handling and argument checking
        TODO: implement limit, orderby, etc.

        :param args:
        :param kwargs:
        :return:
        """

        cur_where = Query(parent=cls._get_collection(),
                          # TODO: pass caught kwargs to Query constructor
                          )

        cur_where = cls._where_query(*args, **kwargs,
                                     cur_where=cur_where)

        if limit is not None:
            cur_where = cur_where.limit(count=limit)

        return cur_where
