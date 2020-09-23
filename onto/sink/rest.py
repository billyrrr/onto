from .base import Sink

import flask


class RestServerSink(Sink):

    def emit_and_close(self, response: flask.Response):
        flask.abort(response)


class RestClientSink(Sink):

    def emit(self, url, data):
        import requests
        requests.post(url=url, data=data)

rest_server = RestServerSink

rest_client = RestClientSink
