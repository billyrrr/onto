from .base import Sink


class Websocket(Sink):

    def __init__(self, namespace):
        self._namespace = namespace

    def emit(self, obj):
        self._namespace.emit("updated", obj.to_view_dict())

websocket = Websocket
