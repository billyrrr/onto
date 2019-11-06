import pytest as pytest

from flask_boiler import schema, fields, domain_model, view_model, factory
from .fixtures import setup_app


class ColorSchema(schema.Schema):
    name = fields.Str()


class ColorDomainModelBase(domain_model.DomainModel):
    _collection_name = "colors"


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