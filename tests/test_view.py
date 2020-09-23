from itertools import count

import pytest as pytest

from onto import schema, fields, view_model

from onto.store.struct import Struct
from tests.color_fixtures import Color, PaletteViewModel, RainbowStoreBpss, color_refs, vm
from .fixtures import CTX


@pytest.fixture
def v_cls(CTX):

    class RainbowSchema(schema.Schema):
        rainbow_name = fields.Raw(dump_only=True)
        colors = fields.Raw(dump_only=True)

    class RainbowView(view_model.ViewModel):

        _schema_cls = RainbowSchema

        _color_d = dict()

        def __init__(self, order_d=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.order = order_d

        @property
        def colors(self):
            return [self._color_d[key] for key in sorted(self._color_d)]

        @property
        def rainbow_name(self):
            return "-".join([self._color_d[key] for key in sorted(self._color_d)])

        def set_color(self, color_name, order):
            self._color_d[(order, color_name)] = color_name

        def get_vm_update_callback(self, dm_cls, *args, **kwargs):
            if issubclass(dm_cls, Color):
                def update_func(vm: RainbowView, dm: Color):
                    order = self.order[dm.doc_id]
                    vm.set_color(dm.name, order=order)
                return update_func

        @classmethod
        def get_from_color_names(cls, color_names):

            struct = Struct(schema_obj=RainbowStoreBpss())

            order_gen = count()
            order_d = dict()

            for color_name in color_names:
                obj_type = Color
                doc_id = "doc_id_{}".format(color_name)

                order_d[doc_id] = next(order_gen)

                struct["colors"][doc_id] = (obj_type, doc_id,)

            return cls.get(struct_d=struct, order_d=order_d, once=True)

    return RainbowView


def test_to_dict_view(v_cls, color_refs):
    vm = v_cls.get_from_color_names(["yellow", "magenta", "cian"])
    # time.sleep(3)
    assert vm.to_view_dict() == {
        'rainbowName': 'yellow-magenta-cian',
        'colors': ['yellow', 'magenta', 'cian']
    }


def test_vm__export_as_view_dict(color_refs, CTX):
    vm = PaletteViewModel.new(
        doc_ref=CTX.db.collection("palettes").document("palette_id_a")
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
