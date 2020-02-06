import pytest as pytest
from google.type.color_pb2 import Color

from flask_boiler import schema, fields, domain_model, view_model, factory
from flask_boiler.business_property_store import BPSchema
from flask_boiler.model_registry import ModelRegistry
from flask_boiler.struct import Struct
from flask_boiler.utils import random_id
from flask_boiler.view_model import ViewModel
from .fixtures import setup_app


class ColorSchema(schema.Schema):
    name = fields.Str()


class ColorDomainModelBase(domain_model.DomainModel):
    _collection_name = "colors"


class RainbowStoreBpss(BPSchema):
    colors = fields.StructuralRef(dm_cls=Color, many=True)


class RainbowSchemaDAV(schema.Schema):
    rainbow_name = fields.Raw(dump_only=True)
    colors = fields.Raw(dump_only=True)


@pytest.fixture
def rainbow_vm(CTX):

    if ModelRegistry.get_cls_from_name("RainbowViewModelDAV") is not None:
        return ModelRegistry.get_cls_from_name("RainbowViewModelDAV")

    class RainbowViewModelDAV(ViewModel):

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

        def set_color(self, color_id, color_name):
            self._color_d[color_id] = color_name

        def get_vm_update_callback(self, dm_cls, *args, **kwargs):

            if dm_cls == Color:
                def callback(vm: RainbowViewModelDAV, dm: Color):
                    vm.set_color(dm.doc_id, dm.name)
                return callback
            else:
                return super().get_vm_update_callback(dm_cls, *args, **kwargs)

        @classmethod
        def create_from_color_names(cls, color_names, once=False, **kwargs):
            struct = Struct(schema_obj=RainbowStoreBpss())
            struct["colors"] = {
                "doc_id_{}".format(color_name):
                    (Color, "doc_id_{}".format(color_name))
                for color_name in color_names
            }

            vm_id = random_id()
            doc_ref = CTX.db.collection("RainbowDAV").document(vm_id)
            return super().get(doc_ref=doc_ref,
                               struct_d=struct,
                               once=once,
                               **kwargs)

        @classmethod
        def new(cls, color_names: str=None, **kwargs):
            color_name_list = color_names.split("+")
            return cls.create_from_color_names(
                color_names=color_name_list,
                **kwargs)

    return RainbowViewModelDAV


@pytest.fixture
def color_refs(request):

    cian = Color.new("doc_id_cian")
    cian.name = 'cian'
    cian.save()

    magenta = Color.new("doc_id_magenta")
    magenta.name = "magenta"
    magenta.save()

    yellow = Color.new("doc_id_yellow")
    yellow.name = "yellow"
    yellow.save()

    black = Color.new("black")
    black.name = "black"
    black.save()

    def fin():
        cian.delete()
        magenta.delete()
        yellow.delete()
        black.delete()

    request.addfinalizer(fin)

    return [cian.doc_ref,
            magenta.doc_ref,
            yellow.doc_ref,
            black.doc_ref
            ]


class Palette(schema.Schema):
    palette_name = fields.Str()
    colors = fields.Relationship(nested=False, many=True)


class PaletteViewModelBase(view_model.ViewModel):
    pass


@pytest.fixture
def vm(color_refs, CTX, request):

    # Create palette document in firestore
    vm = PaletteViewModel.new(
        doc_ref=CTX.db.collection("palettes").document("palette_id_a")
    )
    vm.palette_name = 'cmyk'
    vm.colors = color_refs

    vm.save()

    def fin():
        vm.delete()

    request.addfinalizer(fin)

    return vm


Color = factory.ClsFactory.create(
    name="Color",
    schema=ColorSchema,
    base=ColorDomainModelBase
)
PaletteViewModel = factory.ClsFactory.create(
    name="PaletteViewModel",
    schema=Palette,
    base=PaletteViewModelBase
)