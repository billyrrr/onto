from flask import Response, jsonify

from examples.meeting_room.domain_models import Meeting
from examples.meeting_room.view_models import MeetingSession
from examples.meeting_room.view_models.meeting_session import MeetingSessionC
from onto.source.rest import RestViewModelSource
from onto.view import Mediator

# class RestMediator(Mediator):
#
#     view_model_cls = None
#     source = RestViewModelSource()


class ViewModelResponse(Response):
    pass


class MeetingSessionRest(Mediator):

    # from onto import source, sink

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
