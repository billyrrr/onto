from flask_boiler.context import Context as CTX
from collections import namedtuple
from typing import Optional, Tuple

# from google.cloud.firestore import DocumentSnapshot, CollectionReference
from flask_boiler.fields import argument, OBJ_TYPE_ATTR_NAME
from google.cloud import firestore
from . import cmp
import weakref


class QueryBase:

    def __init__(self, ref=None, path=None, arguments=None):
        if path is not None:
            from flask_boiler.database import Reference
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

    @classmethod
    def _append_new_style(cls, *, cur_arguments=None, **kwargs):
        if cur_arguments is None:
            raise ValueError

        for key, val in kwargs.items():
            comp, other = val if isinstance(val, tuple) else ("==", val)
            cur_arguments.append(
                argument(key=key, comparator=comp, val=other)
            )
        return cur_arguments

    @staticmethod
    def _append_cmp_style(*args, cur_arguments=None):

        if cur_arguments is None:
            raise ValueError

        if len(args) != 0:

            arg_stack = list(args)

            while len(arg_stack) != 0:

                condition = arg_stack.pop(0)
                key = condition.fieldname

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
        arguments = self._append_new_style(
            **kwargs, cur_arguments=arguments)
        return self.make_copy(arguments=arguments)


class Query(QueryBase):
    pass


class ViewModelQuery(QueryBase):

    @classmethod
    def patch_query(cls, parent):
        path = "**/{}_PATCH".format(parent.__name__)
        return cls(parent=parent, path=path)

    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        super().__init__(**kwargs)

    def _to_firestore_query(self):
        """ Returns a query with parent=cls._get_collection(), and
                limits to obj_type of subclass of cls.
        """
        from flask_boiler.database.firestore import FirestoreDatabase

        db: FirestoreDatabase = CTX.db
        if self.ref.first == '**':
            cur_where = db.firestore_client.collection_group(self.ref.last)
        else:
            q = db._doc_ref_from_ref(self.ref)
            cur_where = firestore.Query(parent=q)
        if len(self.arguments) != 0:
            raise ValueError
        return cur_where


class DomainModelQuery(QueryBase):

    # def get_query(self):
    #     """ Returns a query with parent=cls._get_collection(), and
    #             limits to obj_type of subclass of cls.
    #     """
    #     from flask_boiler.database.firestore import FirestoreDatabase
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

    def _to_firestore_query(self):
        """ Returns a query with parent=cls._get_collection(), and
                limits to obj_type of subclass of cls.
        """
        from flask_boiler.database.firestore import FirestoreDatabase

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
        for arg in arguments:
            data_key = self.parent._query_schema().fields[arg.key].data_key
            cur_where = cur_where.where(data_key, arg.comparator, arg.val)
        return cur_where
