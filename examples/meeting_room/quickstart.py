from flasgger import Swagger
from flask import Flask

from examples.meeting_room.view_models import MeetingSession, UserView
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMutation
from examples.meeting_room.views import meeting_session_ops
from onto.view import rest_api

app = Flask(__name__)

meeting_session_mediator = rest_api.ViewMediator(
    view_model_cls=MeetingSession,
    app=app,
    mutation_cls=MeetingSessionMutation
)
meeting_session_mediator.add_list_get(
    rule="/meeting_sessions",
    list_get_view=meeting_session_ops.ListGet
)

meeting_session_mediator.add_instance_get(
    rule="/meeting_sessions/<string:doc_id>")
meeting_session_mediator.add_instance_patch(
    rule="/meeting_sessions/<string:doc_id>")

user_mediator = rest_api.ViewMediator(
    view_model_cls=UserView,
    app=app,
)
user_mediator.add_instance_get(
    rule="/users/<string:doc_id>"
)

swagger = Swagger(app)

if __name__ == "__main__":
    app.run(debug=True)
