class Sink:

    def emit(self):
        pass

    def close(self):
        pass

    def emit_and_close(self, *args, **kwargs):
        pass

    def insert(self):
        pass

    def update(self):
        pass

    def upsert(self):
        pass

    def remove(self):
        pass


import flask


class RestServerSink(Sink):

    def emit_and_close(self, response: flask.Response):
        flask.abort(response)


class RestClientSink(Sink):

    def emit(self, url, data):
        import requests
        requests.post(url=url, data=data)


class Websocket(Sink):

    def __init__(self, namespace):
        self._namespace = namespace

    def emit(self, obj):
        self._namespace.emit("updated", obj.to_view_dict())


class FirestoreSink(Sink):

    def emit(self, snapshot, reference):

        pass

