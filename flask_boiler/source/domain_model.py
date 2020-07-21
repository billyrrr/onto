"""
DomainModel source:
    Invokes a mediator with instantiated domain model
"""
from typing import Type

from google.cloud.firestore_v1 import transactional

from flask_boiler.database import Reference
from flask_boiler.domain_model import DomainModel
from flask_boiler.source.firestore import FirestoreSource
from flask_boiler.context import Context as CTX


class DomainModelSource(FirestoreSource):

    def __init__(self, domain_model_cls: Type[DomainModel]):
        self.domain_model_cls = domain_model_cls
        query = self.domain_model_cls.get_query()
        super().__init__(query=query)

    def _call(self, container):
        for func_name, ref, snapshot in self.delta(container):
            obj = self.domain_model_cls.from_snapshot(
                ref=ref, snapshot=snapshot)
            self._invoke_mediator(func_name=func_name, obj=obj)


class DomainModelTransactionalSource(DomainModelSource):

    def _call(self, container):
        for func_name, ref, snapshot in self.delta(container):
            self._operation(func_name=func_name, ref=ref, snapshot=snapshot)

    def _operation(self, func_name, ref, snapshot):
        _transaction = CTX.db.firestore_client.transaction()
        @transactional
        def _op(transaction):
            obj = self.domain_model_cls.get(
                doc_ref=ref, transaction=transaction)
            self._invoke_mediator(
                func_name=func_name,
                obj=obj,
                transaction=transaction
            )
        _op(_transaction)

class DomainModelPathSource(DomainModelSource):

    def _call(self, ref: Reference):
        doc_id = ref.last
        doc_ref = self.domain_model_cls.ref_from_id(doc_id=doc_id)
        snapshot = CTX.db.get(ref=doc_ref)
        return self.domain_model_cls.from_snapshot(
            ref=doc_ref, snapshot=snapshot)
