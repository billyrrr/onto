from flask import Blueprint, Flask, abort, Response, make_response, jsonify
from tornado.routing import Rule

from examples.meeting_room.domain_models import Meeting
from examples.meeting_room.view_models import MeetingSession
from examples.meeting_room.view_models.meeting_session import MeetingSessionC
from flask_boiler.source.base import Source
from flask_boiler.source.protocol import Protocol
from flask_boiler.view import Mediator


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

    def __init__(self, *args, **kwargs):
        self._mediator_instance = None
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

    def start(self, *args, url_prefix=None, **kwargs):
        if url_prefix is None:
            url_prefix = '/' + self.mediator_instance.view_model_cls._get_collection_name()
        return super().start(*args, url_prefix, **kwargs)


# class RestMediator(Mediator):
#
#     view_model_cls = None
#     source = RestViewModelSource()


class ViewModelResponse(Response):
    pass


class MeetingSessionRest(Mediator):

    # from flask_boiler import source, sink

    view_model_cls = MeetingSessionC

    rest = RestViewModelSource()

    @rest.route('/<doc_id>', methods=('GET',))
    def materialize_meeting_session(self, doc_id):

        meeting = Meeting.get(doc_id=doc_id)

        def notify(obj):
            d = obj.to_snapshot().to_dict()
            content = jsonify(d)
            self.rest.emit(content)

        _ = MeetingSessionC.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )

    # @rest.route('/', methods=('GET',))
    # def list_meeting_ids(self):
    #     return [meeting.to_snapshot().to_dict() for meeting in Meeting.all()]

    @classmethod
    def start(cls, app):
        cls.rest.start(app)
