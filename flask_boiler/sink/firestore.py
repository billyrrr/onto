from flask_boiler.context import Context as CTX
from .base import Sink


class FirestoreSink(Sink):

    def emit(self, reference, snapshot):
        CTX.db.set(ref=reference, snapshot=snapshot)


firestore = FirestoreSink
