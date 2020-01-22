import time

import pytest
from flasgger import SwaggerView, Swagger
from flask import Flask

from flask_boiler import schema, fields, view, domain_model, factory, \
    view_model, view_mediator
from flask_boiler.business_property_store import BPSchema
from flask_boiler.referenced_object import ReferencedObject
from flask_boiler.struct import Struct
from flask_boiler.utils import random_id
from flask_boiler.view_mediator_dav import ViewMediatorDAV
from flask_boiler.view_model import PersistableMixin, ViewModelMixin

from .fixtures import CTX
from .color_fixtures import color_refs, ColorSchema, ColorDomainModelBase, \
    Color, rainbow_vm
from tests.fixtures import setup_app


def test_rainbow_stuffs(CTX, setup_app, color_refs, rainbow_vm):
    app = setup_app
    RainbowViewModelDAV = rainbow_vm

    assert isinstance(app, Flask)

    def notify(self):
        self.save()

    obj = RainbowViewModelDAV.new("yellow+magenta+cian",
                                  f_notify=notify)

    vm_id = obj.doc_ref.id

    # time.sleep(3)

    assert CTX.db.collection("RainbowDAV").document(vm_id).get().to_dict() == {
        'rainbowName': 'cian-magenta-yellow',
        'colors': ['cian', 'magenta', 'yellow'],
        'doc_ref': 'RainbowDAV/{}'.format(vm_id),
        'obj_type': 'RainbowViewModelDAV',
    }
