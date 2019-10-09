import time

import pytest
from flasgger import SwaggerView, Swagger
from flask import Flask

from flask_boiler import schema, fields, view, domain_model, factory, \
    view_model, view_mediator
from flask_boiler.referenced_object import ReferencedObject
from flask_boiler.utils import random_id
from flask_boiler.view_model import PersistableMixin, ViewModelMixin

from .fixtures import CTX
from .color_fixtures import color_refs, ColorSchema, ColorDomainModelBase, Color
from tests.fixtures import setup_app


def test_rainbow_stuffs(CTX, setup_app, color_refs):
    app = setup_app

    assert isinstance(app, Flask)

    vm_id = random_id()

    class RainbowSchemaDAV(schema.Schema):
        rainbow_name = fields.Raw(dump_only=True)
        colors = fields.Raw(dump_only=True)

    class RainbowViewModelDAV(view.DocumentAsView):

        _schema_cls = RainbowSchemaDAV
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

        @classmethod
        def create_from_color_names(cls, color_names):
            struct = dict()

            for color_name in color_names:
                obj_type = "Color"
                doc_id = "doc_id_{}".format(color_name)

                def update_func(vm: RainbowViewModelDAV, dm: Color):
                    vm.set_color(dm.name)

                struct[color_name] = (obj_type, doc_id, update_func)
            doc_ref = CTX.db.collection("RainbowDAV").document(vm_id)
            return super().get(doc_ref=doc_ref, struct_d=struct, once=False)

        @classmethod
        def new(cls, color_names: str=None):
            color_name_list = color_names.split("+")
            return cls.create_from_color_names(color_names=color_name_list)

    obj = RainbowViewModelDAV.new("yellow+magenta+cian")
    time.sleep(3)

    assert CTX.db.collection("RainbowDAV").document(vm_id).get().to_dict() == {
        'rainbowName': 'cian-magenta-yellow',
        'colors': ['cian', 'magenta', 'yellow'],
        'doc_id': '',
        'doc_ref': 'RainbowDAV/{}'.format(vm_id),
        'obj_type': 'RainbowViewModelDAV',
    }