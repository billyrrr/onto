"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView
from src.view import GenericView, register_view_model
from src import fields
from src.schema import Schema
from src.view_model import ViewModel
from google.cloud import firestore
from functools import partial

from src.config import Config
from src.context import Context as CTX

if __name__ == "__main__":
    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )

    CTX.read(config)


    class Color(Schema):
        name = fields.Str()


    class Palette(Schema):
        palette_name = fields.Str()
        colors = fields.Nested(Color, many=True)

    class PaletteViewModel(ViewModel):
        _schema_cls = Palette


    description = "A list of colors (may be filtered by palette)"

    # class PaletteView(GenericView):

    # def __new__(cls, *args, **kwargs):
    #     instance = super().__new__(cls,
    #                                view_model_cls=PaletteViewModel,
    #                                description="A list of colors (may be filtered by palette)"
    #                                )
    #     return instance

    # Create palette document in firestore
    vm = PaletteViewModel.create(
        CTX.db.collection("palettes").document("palette_id_a")
    )
    vm._import_properties({"palette_name": 'cmyk',
                           "colors": [
                               {'name': 'cian'},
                               {'name': 'magenta'},
                               {'name': 'yellow'},
                               {'name': 'black'}
                           ]
                           })

    vm.save()

    app = Flask(__name__)
    swagger = Swagger(app)

    def _mapper(path_str_template: str, _kwargs):
        """

        :param path_str_template: example "company/{}"
        :param args: example ["users"]
        :return: DocumentReference for "company/users"
        """
        """
        Maps a list of arguments from flask.View().get(args) to
            a firestore reference that is used to construct
            the ReferencedObject document
        :return:
        """
        path_str = path_str_template.format(**_kwargs)
        print(path_str)
        path = CTX.db.document(path_str)
        print(path)
        return path

    palette_doc_mapper = partial(_mapper, "palettes/{doc_id}")

    register_view_model(app,
                        view_model_cls=PaletteViewModel,
                        mapper=palette_doc_mapper)

    app.run(debug=True)
