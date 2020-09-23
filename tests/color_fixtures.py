import pytest as pytest
from google.type.color_pb2 import Color

from onto import schema, fields, domain_model, view_model, \
    attrs
from onto.store import reference
from onto.store.store import BPSchema, Store
from onto.registry import ModelRegistry
from onto.store.struct import Struct
from onto.view_model import ViewModel
from onto.models import factory

class ColorSchema(schema.Schema):
    name = fields.Str()


class ColorDomainModelBase(domain_model.DomainModel):
    _collection_name = "colors"


class RainbowStoreBpss(BPSchema):
    colors = fields.StructuralRef(dm_cls=Color, many=True)


@pytest.fixture
def rainbow_vm(CTX):

    if ModelRegistry.get_cls_from_name("RainbowViewModelDAV") is not None:
        return ModelRegistry.get_cls_from_name("RainbowViewModelDAV")

    class RainbowStore(Store):
        colors = reference(dm_cls=Color, many=True, missing=list)


    class RainbowViewModelDAV(ViewModel):

        rainbow_name = attrs.bproperty(import_enabled=False)
        colors = attrs.bproperty(import_enabled=False)

        doc_ref = attrs.bproperty(export_enabled=False)

        # @doc_ref.getter
        # def doc_ref(self):
        #     return self._doc_ref

        obj_type = attrs.bproperty(import_enabled=False, export_enabled=False)

        @colors.getter
        def colors(self):
            return [self.store.colors[key].name for key in sorted(self.store.colors)]

        @rainbow_name.getter
        def rainbow_name(self):
            return "-".join(self.colors)

        @classmethod
        def get(cls, color_names: str=None, once=True, **kwargs):
            color_name_list = color_names.split("+")
            struct = dict()
            struct["colors"] = {
                "doc_id_{}".format(color_name):
                    (Color, "doc_id_{}".format(color_name))
                for color_name in color_name_list
            }
            store = RainbowStore.from_struct(struct=struct)
            vm_id = color_names
            doc_ref = CTX.db.ref/"RainbowDAV"/vm_id
            return super().get(doc_ref=doc_ref,
                               store=store,
                               once=once,
                               **kwargs)

        def save(self):
            CTX.db.set(
                ref=self.doc_ref,
                snapshot=self.to_snapshot()
            )

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
    colors = fields.Relationship(nested=True, many=True)


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


class ColorViewModel(view_model.ViewModel):

    color = attrs.relation(export_enabled=False, nested=True, dm_cls=Color)
    name = attrs.bproperty()

    @name.getter
    def name(self):
        return self.color.name


class PaletteViewModel(view_model.ViewModel):
    palette_name = attrs.bproperty()
    colors = attrs.embed(obj_cls=ColorViewModel, many=True)
    doc_ref = attrs.doc_ref()

    @colors.getter
    def colors(self):
        return [
            ColorViewModel.new(color=Color.get(doc_ref=color_ref))
            for color_ref in self._attrs.colors
        ]


PaletteDomainModel = factory.ClsFactory.create(
    name="PaletteDomainModel",
    schema=Palette,
    base=domain_model.DomainModel
)
