import abc

from onto.context import Context as CTX
from collections import namedtuple
from typing import Optional, Tuple

# from google.cloud.firestore import DocumentSnapshot, CollectionReference
from onto.mapper.fields import argument, OBJ_TYPE_ATTR_NAME
from . import cmp
import weakref


class QueryBase:
    """
    Query depends on Database
    """

    """
    Abstract property: database 
    must override
    """

    def __init__(self, ref=None, path=None, arguments=None):
        if path is not None:
            from onto.database import Reference
            ref = Reference.from_str(path)
        self.ref = ref
        if arguments is None:
            arguments = list()
        self.arguments = arguments

    @staticmethod
    def _append_original(*args, cur_arguments=None):
        if cur_arguments is None:
            raise ValueError

        if len(args) != 0:
            if len(args) % 3 != 0:
                raise ValueError
            else:
                arg_stack = list(args)

                while len(arg_stack) != 0:
                    arg1 = arg_stack.pop(0)
                    arg2 = arg_stack.pop(0)
                    arg3 = arg_stack.pop(0)
                    cur_arguments.append( argument(
                        key=arg1, comparator=arg2, val=arg3
                    ))

        return cur_arguments

    @staticmethod
    def _append_cmp_style(*args, cur_arguments=None):

        if cur_arguments is None:
            raise ValueError

        if len(args) != 0:

            arg_stack = list(args)

            while len(arg_stack) != 0:

                condition = arg_stack.pop(0)

                key = condition.attr_name

                for comp, other in condition.constraints:
                    if comp == "_in":
                        # Reverse argument order for "in" comparator
                        cur_arguments.append( argument(
                            key=other, comparator="in", val=key)
                        )
                    else:
                        # Append comparator for normal cases
                        cur_arguments.append( argument(
                            key=key, comparator=comp, val=other)
                        )

        return cur_arguments

    def make_copy(self, arguments):
        return self.__class__(ref=self.ref, arguments=arguments)

    def where(self, *args, **kwargs):
        cmp_args = [arg for arg in args if isinstance(arg, cmp.Condition)]
        remaining_args = [arg for arg in args
                          if not isinstance(arg, cmp.Condition)]
        arguments = self.arguments.copy()
        arguments = self._append_cmp_style(
            *cmp_args, cur_arguments=arguments)
        arguments = self._append_original(
            *remaining_args, cur_arguments=arguments)
        return self.make_copy(arguments=arguments)


class Query(QueryBase):
    pass


class ViewModelQuery(QueryBase):

    @classmethod
    def patch_query(cls, parent):
        path = "**/{}_PATCH".format(parent.__name__)
        return cls(parent=parent, path=path)

    @classmethod
    def from_view_model(cls, parent):
        ref = parent._get_collection()
        return cls(parent=parent, ref=ref)

    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        super().__init__(**kwargs)

    def _to_firestore_query(self):
        """ Returns a query with parent=cls._get_collection(), and
                limits to obj_type of subclass of cls.
        """
        from onto.database.firestore import FirestoreDatabase

        db: FirestoreDatabase = CTX.db
        if self.ref.first == '**':
            cur_where = db.firestore_client.collection_group(self.ref.last)
        else:
            q = db._doc_ref_from_ref(self.ref)
            from google.cloud import firestore
            cur_where = firestore.Query(parent=q)
        if len(self.arguments) != 0:
            raise ValueError
        return cur_where


class DomainModelQuery(QueryBase):

    # def get_query(self):
    #     """ Returns a query with parent=cls._get_collection(), and
    #             limits to obj_type of subclass of cls.
    #     """
    #     from onto.database.firestore import FirestoreDatabase
    #     db: FirestoreDatabase = CTX.db
    #     from google.cloud import firestore
    #     cur_where = firestore.Query(
    #         parent=db._doc_ref_from_ref(self.parent()._get_collection())
    #     )
    #     condition = self.parent().get_obj_type_condition()
    #     if condition is not None:
    #         cur_where = cur_where.where(*condition)
    #     return cur_where

    def __init__(self, parent=None, ref=None, **kwargs):
        self.parent = parent
        if ref is None:
            ref = self.parent._get_collection()
        super().__init__(ref=ref, **kwargs)

    def make_copy(self, arguments):
        return self.__class__(
            ref=self.ref, parent=self.parent, arguments=arguments)

    def _to_qualifier(self):
        """ Returns a greedy qualifier. Performance aside, it should work.
        """
        condition = self.parent.get_obj_type_condition()
        arguments = [ condition, *self.arguments ]
        def qualifier(snapshot):
            for (key, comparator, val) in arguments:
                if key not in snapshot:
                    continue
                a = snapshot[key]
                if not comparator(a, val):
                    return False
            return True
        return qualifier


    def _to_firestore_query(self):
        """ Returns a query with parent=cls._get_collection(), and
                limits to obj_type of subclass of cls.
        """
        from onto.database.firestore import FirestoreDatabase

        # TODO: move

        db: FirestoreDatabase = CTX.db
        if self.ref.first == '**':
            cur_where = db.firestore_client.collection_group(self.ref.last)
        else:
            cur_where = db._doc_ref_from_ref(self.ref)
        # cur_where = firestore.Query(parent=q)
        condition = self.parent.get_obj_type_condition()
        if condition is not None:
            arguments = self.arguments + [condition]
        else:
            arguments = self.arguments.copy()
        for (key, comparator, val) in arguments:
            # TODO: NOTE: data_key will always be translated
            data_key = self.parent._query_schema().fields[key].data_key
            condition = comparator if isinstance(comparator, str) else comparator.condition
            # TODO: translate val
            cur_where = cur_where.where(data_key, condition, val)
        return cur_where

    def _to_leancloud_query(self):
        from onto.database.leancloud import LeancloudDatabase

        # db: LeancloudDatabase = CTX.dbs.leancloud  # TODO: read db elsewhere

        condition = self.parent.get_obj_type_condition()

        if condition is not None:
            arguments = self.arguments + [condition]
        else:
            arguments = self.arguments.copy()

        cla_str = self.ref.last
        import leancloud
        cla = leancloud.Object.extend(name=cla_str)
        q = cla.query

        for key, comparator, val in arguments:
            data_key = self.parent._query_schema().fields[key].data_key
            func_name = comparator.condition
            f = getattr(q, func_name)
            f(data_key, val)

        return q
