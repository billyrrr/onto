import pytest
from flask import Flask

from flask_boiler import testing_utils
from .fixtures import CTX
from .color_fixtures import color_refs, ColorSchema, ColorDomainModelBase, \
    Color, rainbow_vm
from tests.fixtures import setup_app
from unittest import mock


def test_rainbow_stuffs(CTX, setup_app, color_refs, rainbow_vm):

    RainbowViewModelDAV = rainbow_vm

    def notify(obj):
        obj.save()

    obj = RainbowViewModelDAV.new("yellow+magenta+cian",
                                  f_notify=notify)  # Non-standard usage

    vm_id = obj.doc_ref.id

    assert CTX.db.collection("RainbowDAV").document(vm_id).get().to_dict() == {
        'rainbowName': 'cian-magenta-yellow',
        'colors': ['cian', 'magenta', 'yellow'],
        'doc_ref': 'RainbowDAV/{}'.format(vm_id),
        'obj_type': 'RainbowViewModelDAV',
    }
