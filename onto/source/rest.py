from flask import Blueprint, Flask, abort, Response, make_response, jsonify

from onto.source.base import Source
from onto.source.protocol import Protocol


class RestProtocol(Protocol):
    """
    TODO: remove self.mapping initialized in superclass
    """

    def _register(self, rule, methods):
        def decorator(f):
            self.mapping[(rule, methods)] = f.__name__
            return f
        return decorator

    def fname_of(self, func_name):
        return func_name

    def route(self, *args, **kwargs):
        return self._register(*args, **kwargs)

    def __getattr__(self, item):
        raise AttributeError

    def _get_functions(self):
        for (rule, methods), f_name in self.mapping.items():
            yield rule, methods, f_name


class RestSource(Source):

    _protocol_cls = RestProtocol

    def route(self, *args, **kwargs):
        return self.protocol.route(*args, **kwargs)
        # protocol: RestProtocol = self.protocol

    def __init__(self, view_model_cls=None, *args, **kwargs):
        self._mediator_instance = None
        self._view_model_cls = view_model_cls
        super().__init__(*args, **kwargs)

    def emit(self, res):
        abort(res)

    @property
    def mediator_instance(self):
        if self._mediator_instance is None:
            self._mediator_instance = self.parent()()
        return self._mediator_instance

    def start(self, app: Flask, url_prefix=None):
        bp = Blueprint(self.parent().__name__, __name__, url_prefix=url_prefix)
        for rule, methods, f_name in self.protocol._get_functions():
            def routable(*args, **kwargs):
                return self._invoke_mediator(func_name=f_name, *args,  **kwargs)
            bp.add_url_rule(rule=rule, view_func=routable, methods=methods)
        app.register_blueprint(bp)


class RestViewModelSource(RestSource):

    @property
    def view_model_cls(self):
        if self._view_model_cls is not None:
            return self._view_model_cls
        else:
            return self.mediator_instance.view_model_cls

    def start(self, *args, url_prefix=None, **kwargs):
        if url_prefix is None:
            url_prefix = '/' + self.view_model_cls._get_collection_name()
        return super().start(*args, url_prefix, **kwargs)

