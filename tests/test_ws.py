"""
Tests Websocket integration

"""

import pytest
from unittest.mock import MagicMock, patch
from flask_boiler.view_mediator_websocket import ViewMediatorWebsocket
from .color_fixtures import Color, PaletteViewModel
from .fixtures import setup_app, CTX
import flask_socketio
import time


def test_connect(setup_app):
    app = setup_app

    class Demo(ViewMediatorWebsocket):
        pass

    mediator = Demo(view_model_cls=PaletteViewModel,
                    mutation_cls=None,
                    namespace="/palette")

    io = flask_socketio.SocketIO(app=app)

    io.on_namespace(mediator)

    client = io.test_client(app=app, namespace='/palette')

    assert client.is_connected(namespace='/palette') is True

    print(io.namespace_handlers)

    res = client.emit('subscribe_view_model', {"hello": "world"},
                      namespace='/palette')

    assert client.get_received(namespace="/palette") == [
        {'name': 'message', 'args': 'connected', 'namespace': '/palette'},
        {'name': 'message', 'args': '{}', 'namespace': '/palette'},
        {'name': 'message', 'args': '{}', 'namespace': '/palette'},
        {'name': 'my custom namespace response',
         'args': [{'hello': 'world'}], 'namespace': '/palette'}]
