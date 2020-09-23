# from onto.store.snapshot_container import SnapshotContainer
# from onto.store.struct import Struct
# from .color_fixtures import Color, PaletteDomainModel
# from onto import fields
# from onto.store.business_property_store import BusinessPropertyStore, BPSchema
# import pytest
#
#
# class SomeSchema(BPSchema):
#     favorite_color = fields.StructuralRef(dm_cls=Color)
#
#
# @pytest.mark.usefixtures("CTX")
# def test_get_manifest(color_refs):
#
#     cian_id = color_refs[0].id
#
#     struct = Struct(schema_obj=SomeSchema())
#     struct["favorite_color"] = (Color, cian_id)
#
#     g, gr, manifest = BusinessPropertyStore._get_manifests(struct, SomeSchema())
#
#     assert g == {
#         "favorite_color": 'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian'
#     }
#     assert gr == {
#         'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian': ["favorite_color"]
#     }
#     assert manifest == {
#         (Color, 'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian'),
#     }
#
#
# def test_update(CTX, color_refs):
#     cian_id = color_refs[0].id
#     struct = Struct(schema_obj=SomeSchema())
#     struct["favorite_color"] = (Color, cian_id)
#
#     class Store(BusinessPropertyStore):
#         pass
#
#     store = Store(struct=struct, snapshot_container=SnapshotContainer())
#     store._container.set(
#         'projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian',
#             CTX.db.document('projects/flask-boiler-testing/databases/(default)/documents/colors/doc_id_cian').get()
#     )
#     store.refresh()
#     assert isinstance(store.favorite_color, Color)
#
#
# def test_obj_options(CTX, color_refs, request):
#     palette = PaletteDomainModel.new(
#         doc_id="partial_rainbow_palette",
#         palette_name="partial_rainbow",
#         colors=color_refs.copy()
#     )
#     palette.save()
#
#     def fin():
#         palette.delete()
#
#     request.addfinalizer(fin)
#
#     class PaletteStoreSchema(BPSchema):
#         favorite_palette = fields.StructuralRef(dm_cls=PaletteDomainModel)
#
#     struct = Struct(schema_obj=PaletteStoreSchema())
#     struct["favorite_palette"] = (PaletteDomainModel, palette.doc_id)
#
#     class Store(BusinessPropertyStore):
#         pass
#
#     """
#     Original: non-nested retrieves DocumentReference
#     """
#
#     store = Store(
#         struct=struct,
#         snapshot_container=SnapshotContainer()
#     )
#     store._container.set(
#         'projects/flask-boiler-testing/databases/(default)/documents/PaletteDomainModel/partial_rainbow_palette',
#             CTX.db.document('projects/flask-boiler-testing/databases/(default)/documents/PaletteDomainModel/partial_rainbow_palette').get()
#     )
#     store.refresh()
#     assert isinstance(store.favorite_palette, PaletteDomainModel)
#     assert isinstance(store.favorite_palette.colors[0], Color)
#
#     # """
#     # New: nested retrieves objects
#     # """
#     # store = Store(
#     #     struct=struct,
#     #     snapshot_container=SnapshotContainer(),
#     #     obj_options=dict(
#     #         must_get=True
#     #     )
#     # )
#     # store._container.set(
#     #     'projects/flask-boiler-testing/databases/(default)/documents/PaletteDomainModel/partial_rainbow_palette',
#     #     CTX.db.document(
#     #         'projects/flask-boiler-testing/databases/(default)/documents/PaletteDomainModel/partial_rainbow_palette').get()
#     # )
#     # store.refresh()
#     # assert isinstance(store.favorite_palette, PaletteDomainModel)
#     # assert isinstance(store.favorite_palette.colors[0], Color)
