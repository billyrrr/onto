from .color_fixtures import color_refs, Color
from .fixtures import CTX
from flask_boiler.business_property_store import BusinessPropertyStore
import pytest


@pytest.mark.usefixtures("CTX")
def test_get_manifest(color_refs):

    cian_id = color_refs[0].id

    struct = {
        "favorite_color": (Color, cian_id)
    }

    g, gr, manifest = BusinessPropertyStore._get_manifests(struct)

    assert g == {
        "favorite_color": 'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian'
    }
    assert gr == {
        'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian': ["favorite_color"]
    }
    assert manifest == {'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian', }


def test_update(CTX, color_refs):
    cian_id = color_refs[0].id
    struct = {
        "favorite_color": (Color, cian_id)
    }
    store = BusinessPropertyStore(struct)
    store._container.set(
        'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian',
            CTX.db.document('projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian').get()
    )

    assert isinstance(store.favorite_color, Color)

