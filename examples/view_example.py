"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView
from src.view import GenericView
from src import fields
from src.schema import Schema
from src.view_model import ViewModel
from google.cloud import firestore

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


    def register_view_model(app, view_model_cls):
        # Note that there are better ways of implementing this
        _proxy_view_cls_name = "{}ProxyView".format(view_model_cls.__name__)

        responses = {
            200: {
                "description": description,
                "schema": view_model_cls.get_schema_cls()
            }
        }

        parameters = [
            {
                "name": "doc_id",
                "in": "path",
                "type": "string",
                "enum": ["all", "palette_id_a",
                         "palette_id_b"],
                "required": True,
                "default": "all"
            }
        ]

        def get(self, doc_id):
            doc_ref: firestore.DocumentReference = \
                CTX.db.collection("palettes").document(doc_id)

            obj = self._view_model_cls.get(doc_ref)
            return jsonify(obj.to_dict())

        # Dynamically construct a proxy class that has responses static var
        proxy_view_cls = type(_proxy_view_cls_name,  # class name
                              (SwaggerView,),
                              dict(responses=responses,
                                   parameters=parameters,
                                   _view_model_cls=view_model_cls,
                                   get=get
                                   )
                              )

        app.add_url_rule(
            '/palettes/<doc_id>',
            view_func=proxy_view_cls.as_view('colors'),
            methods=['GET']
        )


    register_view_model(app, PaletteViewModel)

    app.run(debug=True)
