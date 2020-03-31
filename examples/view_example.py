"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""

from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView
from flask_boiler.view import GenericView, document_as_view, default_mapper
from flask_boiler import fields
from flask_boiler.schema import Schema
from flask_boiler.firestore_object import FirestoreObjectClsFactory
from flask_boiler.view_model import ViewModel
from google.cloud import firestore
from functools import partial

from flask_boiler.config import Config
from flask_boiler.context import Context as CTX

if __name__ == "__main__":
    """
    Go to http://127.0.0.1:5000/apidocs/ for the auto-generated 
        documentations. 
    """

    if CTX.config is None:
        config = Config(
            app_name="flask-boiler-testing",
            debug=True,
            testing=True,
            certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
        )
        CTX.read(config)


    class Color(Schema):
        name = fields.Str()


    class Palette(Schema):
        palette_name = fields.Str()
        colors = fields.Nested(Color, many=True)

    PaletteViewModel = FirestoreObjectClsFactory.create(
        name="PaletteViewModel",
        schema=Palette,
        base=ViewModel
    )

    description = "A list of colors (may be filtered by palette)"

    # Create palette document in firestore
    vm = PaletteViewModel.new(
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

    palette_doc_mapper = partial(default_mapper, "palettes/{doc_id}")

    obj = document_as_view(
                        view_model_cls=PaletteViewModel,
                        app=app,
                        endpoint="/palettes/<string:doc_id>",
                        mapper=palette_doc_mapper)

    app.run(debug=True)
