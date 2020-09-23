from onto.context import Context as CTX
from .base import Sink


class FirestoreSink(Sink):

    def emit(self, reference, snapshot):
        CTX.db.set(ref=reference, snapshot=snapshot)


class ViewModelSink(Sink):

    def emit(self, obj):
        CTX.db.set(ref=obj.doc_ref, snapshot=obj.to_snapshot())


class FormSink(ViewModelSink):

    def emit(self, view_model_obj):
        view_model_obj.propagate_change()


class DomainModelSink(FirestoreSink):

    def emit(self, obj, **kwargs):
        obj.save(**kwargs)

