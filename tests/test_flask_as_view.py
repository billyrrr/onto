import time

import pytest
from flasgger import SwaggerView, Swagger
from flask import Flask

from flask_boiler import schema, fields, view, domain_model, factory, \
    view_model, view_mediator

from .fixtures import CTX
from .color_fixtures import color_refs, ColorSchema, ColorDomainModelBase, Color
from tests.fixtures import setup_app


def test_rainbow_stuffs(CTX, setup_app, color_refs):
    app = setup_app

    assert isinstance(app, Flask)

    test_client = app.test_client()

    class RainbowSchema(schema.Schema):
        rainbow_name = fields.Raw(dump_only=True)
        colors = fields.Raw(dump_only=True)

    class RainbowViewModel(view.FlaskAsView):

        _schema_cls = RainbowSchema
        _color_d = dict()

        @property
        def colors(self):
            res = list()
            for key in sorted(self._color_d):
                res.append(self._color_d[key])
            return res

        @property
        def rainbow_name(self):
            res = list()
            for key in sorted(self._color_d):
                res.append(self._color_d[key])
            return "-".join(res)

        def set_color(self, color_name):
            self._color_d[color_name] = color_name

        def get_vm_update_callback(self, dm_cls, *args, **kwargs):
            def update_func(vm: RainbowViewModel, dm: Color):
                vm.set_color(dm.name)
            return update_func

        @classmethod
        def get_from_color_names(cls, color_names):
            struct = dict()

            for color_name in color_names:
                obj_type = Color
                doc_id = "doc_id_{}".format(color_name)

                struct[color_name] = (obj_type, doc_id)
            return super().get(struct_d=struct, once=True)

        @classmethod
        def new(cls, color_names: str=None):
            color_name_list = color_names.split("+")
            return cls.get_from_color_names(color_names=color_name_list)

    mediator = view_mediator.ViewMediator(
        view_model_cls=RainbowViewModel,
        app=app
    )
    mediator.add_instance_get(rule="/rainbow/<string:color_names>")

    time.sleep(1)

    res = test_client.get(
        path="/rainbow/yellow+magenta+cian")

    assert res.json == {
        'rainbowName': 'cian-magenta-yellow',
        'colors': ['cian', 'magenta', 'yellow']
    }
