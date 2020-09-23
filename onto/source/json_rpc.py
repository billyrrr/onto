from flask import Flask, Blueprint

from .base import Source

from flask_jsonrpc import JSONRPC


class JsonRpcSource(Source):

    def __init__(self, *args, url_prefix, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_prefix = url_prefix

    def start(self, app: Flask):
        jsonrpc = JSONRPC(app, self.url_prefix, enable_web_browsable_api=True)
        for rule, f_name in self.protocol.mapping.items():
            wrapper = jsonrpc.method(name=rule, validate=False)
            @wrapper
            def routable(*args, **kwargs):
                return self._invoke_mediator(func_name=rule, *args,  **kwargs)
