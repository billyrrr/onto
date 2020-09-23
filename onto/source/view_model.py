"""
ViewModel source:
    Invokes a mediator with instantiated view model

Example: invoke on_create when a form is submitted to a collection
    owned by a user.
"""
from typing import Type

from onto.view_model import ViewModel
from onto.query.query import QueryBase
from onto.source.firestore import FirestoreSource


class ViewModelSource(FirestoreSource):

    def __init__(self, view_model_cls: Type[ViewModel], query: QueryBase):
        self.view_model_cls = view_model_cls
        super().__init__(query=query)

    def _call(self, container):
        for change_type_str, ref, snapshot in self.delta(container):
            obj = self.view_model_cls.from_snapshot(
                ref=ref, snapshot=snapshot)
            self._invoke_mediator(func_name=change_type_str, obj=obj)

