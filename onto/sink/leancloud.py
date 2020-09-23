from onto.context import Context as CTX
from .base import Sink


class LcSink(Sink):

    def emit(self, ref, snapshot):
        CTX.dbs.leancloud.set(ref=ref, snapshot=snapshot)


class ViewModelSink(Sink):

    def emit(self, obj):
        CTX.dbs.leancloud.set(ref=obj.doc_ref, snapshot=obj.to_snapshot())
