from unittest import mock
from unittest.mock import Mock, patch

import flask
import pytest

from flask import Flask
from onto import auth

import flask_restful
from flask_restful import Resource, ResponseBase
from firebase_admin import auth as firebase_admin_auth
import firebase_admin

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

    flask_app = flask.app.Flask(__name__)
    api = flask_restful.Api(flask_app)
    api.add_resource(IntegerResource, "/int_resource")
    app = flask_app.test_client()

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


@pytest.fixture
def vit(monkeypatch):
    # mock_auth = Mock()

    verify_id_token = Mock(
        return_value={
            "uid": "uid_1"
        })
    monkeypatch.setattr(
        firebase_admin_auth,
        "verify_id_token",
        verify_id_token
    )
    return verify_id_token


@pytest.fixture
def MockProductionCTX(CTX, monkeypatch):

    monkeypatch.setattr(
        CTX.config, "TESTING", False
    )


def test_authenticate(MockProductionCTX, vit):

    class IntegerResource(Resource):

        @auth.authenticate
        def get(self, uid):
            assert uid == "uid_1"

    flask_app = flask.app.Flask(__name__)
    api = flask_restful.Api(flask_app)
    api.add_resource(IntegerResource, "/int_resource")
    app = flask_app.test_client()

    res = app.get(
        path="/int_resource",
        headers={
            'Authorization': "correct_id_token_for_uid_1"
        }
    )

    assert vit.call_args[0][0] == "correct_id_token_for_uid_1"


def test_authenticate_testing_config(CTX, vit):
    """ Tests that auth is skipped when CTX.testing is True
    :param CTX:
    :param vit:
    :return:
    """

    class IntegerResource(Resource):

        @auth.authenticate
        def get(self, uid):
            assert uid == "uid_1"

    flask_app = flask.app.Flask(__name__)
    api = flask_restful.Api(flask_app)
    api.add_resource(IntegerResource, "/int_resource")
    app = flask_app.test_client()

    res = app.get(
        path="/int_resource",
        headers={
            'Authorization': "uid_1"
        }
    )

    assert vit.call_count == 0


@pytest.fixture
def vit_bomb(monkeypatch):

    def auth_bomb(*args, **kwargs):
        raise firebase_admin_auth.RevokedIdTokenError("mock message")

    verify_id_token = Mock(wraps=auth_bomb)
    monkeypatch.setattr(
        firebase_admin_auth,
        "verify_id_token",
        verify_id_token
    )
    return verify_id_token


def test_authenticate_error(MockProductionCTX, vit_bomb):

    class IntegerResource(Resource):

        @auth.authenticate
        def get(self, uid):
            assert uid == "uid_1"

    flask_app = flask.app.Flask(__name__)
    api = flask_restful.Api(flask_app)
    api.add_resource(IntegerResource, "/int_resource")
    app = flask_app.test_client()

    res = app.get(
        path="/int_resource",
        headers={
            'Authorization': "correct_id_token_for_uid_1"
        }
    )

    assert res.status_code == 401

