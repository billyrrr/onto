from flask_boiler.fields import argument, OBJ_TYPE_ATTR_NAME
from flask_boiler.query import cmp
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.context import Context as CTX

from google.cloud import firestore


def is_fb_snapshot(snapshot: firestore.DocumentSnapshot) -> bool:
    """
    Returns true if a snapshot is generated by flask-boiler
        (checks if obj_type exists)

    :param snapshot:
    :return:
    """
    try:
        _ = snapshot.get("obj_type")
        return True
    except KeyError as ke:
        return False


def convert_query_ref(func):
    """
    Converts a generator of firestore DocumentSnapshot's to a generator
            of objects.

    :param super_cls:
    """
    def call(cls, *args, **kwargs):
        query_ref = func(cls, *args, **kwargs)
        for res in query_ref.stream():
            assert isinstance(res, firestore.DocumentSnapshot)
            # if is_fb_snapshot(snapshot=res):
            #     # Skip this snapshot if it is not generated by flask-boiler
            from flask_boiler.database.firestore import FirestoreSnapshot
            yield snapshot_to_obj(snapshot=res, super_cls=cls)
    return call


def convert_query(func):
    def call(cls, *args, **kwargs):
        q = func(cls, *args, **kwargs)
        for ref, snapshot in CTX.db.query(q):
            yield snapshot_to_obj(
                snapshot=snapshot, doc_ref=ref, super_cls=cls)
    return call


class QueryMixin:

    @classmethod
    @convert_query
    def all(cls):
        """ Gets object that is a subclass of the current cls in
                the collection.
        """

        return cls.get_query()

    @classmethod
    @convert_query
    def where(cls, *args, **kwargs):
        return cls.get_query().where(*args, **kwargs)

    @classmethod
    def get_obj_type_condition(cls):
        schema_obj = cls.get_schema_obj()
        if OBJ_TYPE_ATTR_NAME not in schema_obj.fields:
            return None
        else:
            return schema_obj.fields[OBJ_TYPE_ATTR_NAME]\
                .get_obj_type_condition(cls)

    @classmethod
    def get_query(cls):
        """ Returns a query with parent=cls._get_collection(), and
                limits to obj_type of subclass of cls.
        """

        from flask_boiler.query.query import Query
        return Query(parent=cls)

    # @classmethod
    # @convert_query_ref
    # def where(cls, *args,
    #           acsending=None,
    #           descending=None,
    #           end_at=None,
    #           end_before=None,
    #           limit=None,
    #           offset=None,
    #           order_by=None,
    #           select=None,
    #           start_after=None,
    #           start_at=None,
    #           **kwargs,):
    #     """ Queries the datastore. Note that indexes may need to be added
    #             from the link provided by firestore in the error messages.
    #
    #     NOTE: all subclasses of the current class will be queried
    #     NOTE: this method will fail when the descendents of the class
    #         plus itself counts to >10 due to Firestore query limitation.
    #         (10 "in" queries max, which is 9 descendant classes max).
    #         Watch for dynamically constructed class
    #         in runtime, as this may increase the number of descendants of its
    #         superclass, and may result in fail. To turn off obj_type behavior,
    #         use a separate collection for each class and/or customize
    #         obj_type field/attribute.
    #
    #     TODO: post more examples for customizing obj_type field/attribute
    #
    #     TODO: add error handling and argument checking
    #     TODO: implement limit, orderby, etc.
    #
    #     :param args:
    #     :param kwargs:
    #     """
    #
    #     cur_where = cls._where_query(*args, **kwargs,
    #                                  cur_where=cls.get_query())
    #
    #     if limit is not None:
    #         cur_where = cur_where.limit(count=limit)
    #
    #     return cur_where

