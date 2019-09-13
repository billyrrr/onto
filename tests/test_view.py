from functools import partial

import pytest as pytest

from flask_boiler import schema, fields, factory, view_model, domain_model

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView

from flask_boiler.view import default_mapper, document_as_view
from .fixtures import CTX


class ColorSchema(schema.Schema):
    name = fields.Str()


class ColorDomainModelBase(domain_model.DomainModel):
    _collection_name = "colors"


Color = factory.ClsFactory.create(
    name="Color",
    schema=ColorSchema,
    base=ColorDomainModelBase
)


@pytest.fixture
def color_refs(request):

    cian = Color.create("doc_id_cian")
    cian.name = 'cian'
    cian.save()

    magenta = Color.create("doc_id_magenta")
    magenta.name = "magenta"
    magenta.save()

    yellow = Color.create("doc_id_yellow")
    yellow.name = "yellow"
    yellow.save()

    black = Color.create("black")
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


PaletteViewModel = factory.ClsFactory.create(
    name="PaletteViewModel",
    schema=Palette,
    base=PaletteViewModelBase
)


@pytest.fixture
def vm(color_refs, CTX, request):

    # Create palette document in firestore
    vm = PaletteViewModel.create(
        CTX.db.collection("palettes").document("palette_id_a")
    )
    vm.palette_name = 'cmyk'
    vm.colors = color_refs

    vm.save()

    def fin():
        vm.delete()

    request.addfinalizer(fin)

    return vm


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


@pytest.fixture
def setup_app(vm, CTX):

    description = "A list of colors (may be filtered by palette)"

    app = Flask(__name__)
    swagger = Swagger(app)

    palette_doc_mapper = partial(default_mapper, "palettes/{doc_id}")

    obj = document_as_view(
        view_model_cls=PaletteViewModel,
        app=app,
        endpoint="/palettes/<string:doc_id>",
        mapper=palette_doc_mapper)

    return app


def test_get(setup_app):
    app = setup_app

    assert isinstance(app, Flask)

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

