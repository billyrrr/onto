"""
DomainModel source:
    Invokes a mediator with instantiated domain model
"""
from typing import Type

from flask_boiler.domain_model import DomainModel
from flask_boiler.source.firestore import FirestoreSource


class DomainModelSource(FirestoreSource):

    def __init__(self, domain_model_cls: Type[DomainModel]):
        self.domain_model_cls = domain_model_cls
        query = self.domain_model_cls.get_query()
        super().__init__(query=query)

    def _call(self, container):
        for func_name, ref, snapshot in self.delta(container):
            obj = self.domain_model_cls.from_snapshot(
                ref=ref, snapshot=snapshot)
            fname = self.protocol.fname_of(func_name)
            f = getattr(self.parent()(), fname)
            f(obj=obj)
