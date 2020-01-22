import time

import pytest
from flasgger import SwaggerView, Swagger
from flask import Flask

from flask_boiler import schema, fields, view, domain_model, factory, \
    view_model, view_mediator

from .fixtures import CTX
from .color_fixtures import color_refs, ColorSchema, ColorDomainModelBase, \
    Color, rainbow_vm
from tests.fixtures import setup_app


def test_rainbow_stuffs(CTX, setup_app, color_refs, rainbow_vm):
    app = setup_app

    assert isinstance(app, Flask)

    test_client = app.test_client()

    class RainbowViewModel(rainbow_vm):
       pass

    mediator = view_mediator.ViewMediator(
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
