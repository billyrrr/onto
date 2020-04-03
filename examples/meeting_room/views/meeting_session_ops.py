import time

from flasgger import SwaggerView
from flask import request
from flask.json import jsonify

from examples.meeting_room.view_models import MeetingSession


class ListGet(SwaggerView):

    tags = ["MeetingSession"]

    description = "List all meeting sessions "

    responses = {
            200: {
                "description": description,
                "schema": MeetingSession.get_schema_cls()
            }
        }

    def get(self, *args, **kwargs):
        query_d = request.args.to_dict()
        meeting_sessions = MeetingSession.get_many_from_query(
            query_d=query_d, once=False)
        # time.sleep(1)  # TODO: delete after implementing sync
        results = {meeting_session.meeting_id: meeting_session.to_view_dict()
                   for meeting_session in meeting_sessions}
        return jsonify({
            "results": results
        })
