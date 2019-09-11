import flask
import pytest

from flask_boiler import auth
import flask_restful
from flask_restful import Resource, ResponseBase

from .fixtures import CTX


def get_mock_auth_headers(uid="testuid1"):
    # user = auth.get_user(uid)
    # userIdToken = user.tokens_valid_after_timestamp
    # # userIdToken = auth.create_custom_token(uid=uid, app=firebaseApp)
    # userIdTokenMock = userIdToken
    # warnings.warn("Note that userIdTokenMock is temporary and the test may fail when the token is no longer valid.")
    user_id_token_mock = uid  # For mocking decoding token as uid
    headers = {'Authorization': user_id_token_mock}
    return headers


# @pytest.mark.usefixtures("CTX")
def test_auth(CTX):
    assert CTX.debug

    class IntegerResource(Resource):

        @auth.authenticate
        def get(self, uid):
            assert uid == "test_user_id_2"

    app = flask_restful.app.Flask(__name__).test_client()

    app.add_resource("int_resource/", IntegerResource)

    app.get(
        path="int_resource/",
        headers=get_mock_auth_headers(uid="test_user_id_2"))


def test_auth_no_headers(CTX):

    assert CTX.debug

    class IntegerResource(Resource):

        @auth.authenticate
        def get(self, uid):
            assert uid == "test_user_id_2"

    flask_app = flask.app.Flask(__name__)
    api = flask_restful.Api(flask_app)
    api.add_resource(IntegerResource, "/int_resource")
    app = flask_app.test_client()

    res = app.get(path="/int_resource")

    assert res.status_code == 401

