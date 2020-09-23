from onto.sink.base import Sink


class JsonRpcSink(Sink):

    def __init__(self, *args, uri, **kwargs):
        self.uri = uri
        super().__init__(*args, **kwargs)

    def emit(self, method, **kwargs):
        from jsonrpcclient import request
        response = request(self.uri, method, **kwargs)
        return response

sink = JsonRpcSink

