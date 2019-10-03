import time
from functools import partial
from itertools import count

import pytest as pytest

from flask_boiler import schema, fields, view_model, view

from flask import Flask

from tests.color_fixtures import Color, PaletteViewModel, vm, color_refs
from tests.fixtures import setup_app
from .fixtures import CTX

from flask_boiler.view import default_mapper, document_as_view


@pytest.fixture
def v_cls(CTX):

    class RainbowSchema(schema.Schema):
        rainbow_name = fields.Raw(dump_only=True)
        colors = fields.Raw(dump_only=True)

    class RainbowView(view.FlaskAsViewMixin, view_model.ViewModel):

        _schema_cls = RainbowSchema

        _color_d = dict()

        @property
        def colors(self):
            return [self._color_d[key] for key in sorted(self._color_d)]

        @property
        def rainbow_name(self):
            return "-".join([self._color_d[key] for key in sorted(self._color_d)])

        def set_color(self, color_name, order):
            self._color_d[(order, color_name)] = color_name

        @classmethod
        def get_from_color_names(cls, color_names):
            struct = dict()

            order = count()
            for color_name in color_names:
                obj_type = "Color"
                doc_id = "doc_id_{}".format(color_name)

                def update_func(order, vm: RainbowView, dm: Color):
                    vm.set_color(dm.name, order=order)

                update_func = partial(update_func, order=next(order))

                struct[color_name] = (obj_type, doc_id, update_func)
            return super().get(struct_d=struct)

    return RainbowView


def test_to_dict_view(v_cls, color_refs):
    vm = v_cls.get_from_color_names(["yellow", "magenta", "cian"])
    time.sleep(3)
    assert vm.to_view_dict() == {
        'rainbowName': 'yellow-magenta-cian',
        'colors': ['yellow', 'magenta', 'cian']
    }


def test_vm__export_as_view_dict(color_refs, CTX):
    vm = PaletteViewModel.create(
        CTX.db.collection("palettes").document("palette_id_a")
    )
    vm.palette_name = 'cmyk'
    vm.colors = color_refs
    assert vm.to_dict() == {
        "paletteName": 'cmyk',
        "colors": [
            {'name': 'cian'},
            {'name': 'magenta'},
            {'name': 'yellow'},
            {'name': 'black'}
        ]
    }


def test_vm(vm: PaletteViewModel):
    assert vm.to_dict() == {
        "paletteName": 'cmyk',
        "colors": [
            {'name': 'cian'},
            {'name': 'magenta'},
            {'name': 'yellow'},
            {'name': 'black'}
        ]
    }


@pytest.mark.skip
def test_dav_get(setup_app, vm):
    """ Tests document-as-view (dav) get

    :param setup_app:
    :param vm:
    :return:
    """
    app = setup_app

    assert isinstance(app, Flask)

    description = "A list of colors (may be filtered by palette)"

    palette_doc_mapper = partial(default_mapper, "palettes/{doc_id}")

    obj = document_as_view(
        view_model_cls=PaletteViewModel,
        app=app,
        endpoint="/palettes/<string:doc_id>",
        mapper=palette_doc_mapper)

    test_client = app.test_client()

    res = test_client.get(
        path="/palettes/palette_id_a")

    assert res.status_code == 200
    assert res.json == {
        "paletteName": 'cmyk',
        "colors": [
            {'name': 'cian'},
            {'name': 'magenta'},
            {'name': 'yellow'},
            {'name': 'black'}
        ]
    }

