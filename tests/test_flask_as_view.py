from flask import Flask

from .fixtures import CTX, setup_app
from .color_fixtures import color_refs, rainbow_vm
from onto.view import rest_api


def test_rainbow_stuffs(CTX, setup_app, color_refs, rainbow_vm):
    app = setup_app

    assert isinstance(app, Flask)

    test_client = app.test_client()

    class RainbowViewModel(rainbow_vm):
       pass

    mediator = rest_api.ViewMediator(
        view_model_cls=RainbowViewModel,
        app=app
    )
    mediator.add_instance_get(rule="/rainbow/<string:color_names>")

    # time.sleep(1)

    res = test_client.get(
        path="/rainbow/yellow+magenta+cian")

    assert res.json == {
        'rainbowName': 'cian-magenta-yellow',
        'colors': ['cian', 'magenta', 'yellow']
    }
