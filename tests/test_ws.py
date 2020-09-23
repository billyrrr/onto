"""
Tests Websocket integration

"""

import pytest
from unittest.mock import MagicMock, patch

from onto import testing_utils
from onto.view import WsMediator
from .color_fixtures import Color, PaletteViewModel, rainbow_vm, color_refs
from .fixtures import setup_app, CTX
import flask_socketio
import time


@pytest.mark.skip
def test_connect(setup_app, rainbow_vm, color_refs):
    app = setup_app

    class Demo(WsMediator):
        pass

    mediator = Demo(view_model_cls=rainbow_vm,
                    mutation_cls=None,
                    namespace="/palette")

    io = flask_socketio.SocketIO(app=app)

    io.on_namespace(mediator)

    client = io.test_client(app=app, namespace='/palette')

    assert client.is_connected(namespace='/palette') is True

    res = client.emit('subscribe_view_model',
                      {"color_names": "cian+magenta+yellow"},
                      namespace='/palette')

    assert client.get_received(namespace="/palette") == \
           [{'args': 'connected', 'name': 'message', 'namespace': '/palette'},
            {'args': '{}', 'name': 'message', 'namespace': '/palette'},
            {'args': '{}', 'name': 'message', 'namespace': '/palette'},
            {'args': [], 'name': 'subscribed', 'namespace': '/palette'},
            {'args': [{'colors': ['cian', 'magenta', 'yellow'],
                       'rainbowName': 'cian-magenta-yellow'}],
             'name': 'updated',
             'namespace': '/palette'}]

    color_refs[0].update({"name": "cyan"})

    testing_utils._wait(factor=.7)

    assert client.get_received(namespace="/palette") == [{'name': 'updated', 'args': [{'colors': ['cyan', 'magenta', 'yellow'], 'rainbowName': 'cyan-magenta-yellow'}], 'namespace': '/palette'}]

