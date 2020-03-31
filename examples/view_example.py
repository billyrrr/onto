"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""
import pytest
from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView

from flask_boiler.factory import ClsFactory
from flask_boiler.view import FlaskAsView
from flask_boiler import fields, view_mediator
from flask_boiler.schema import Schema
from flask_boiler.firestore_object import FirestoreObjectClsFactory
from flask_boiler.view_model import ViewModel
from google.cloud import firestore
from functools import partial


class Color(Schema):
    name = fields.Str()


class Palette(Schema):
    case_conversion = False

    palette_name = fields.Str()
    colors = fields.Nested(Color, many=True)


PaletteViewModelBase = ClsFactory.create(
    name="PaletteViewModelBase",
    schema=Palette,
    base=ViewModel
)

repo = {

    "doc_id_1": dict(palette_name='cmyk',
                     colors=[
                         {'name': 'cian'},
                         {'name': 'magenta'},
                         {'name': 'yellow'},
                         {'name': 'black'}
                     ], )
}


class PaletteViewModel(PaletteViewModelBase):
    description = "A list of colors (may be filtered by palette)"

    @classmethod
    def new(cls, *args, doc_id, once=True, **kwargs):
        """
        Hard code a palette. (Not standard usage)
        """
        assert once
        obj = super().new(
            *args,
            **repo[doc_id],
            **kwargs
        )
        return obj


obj = PaletteViewModel.new(doc_id="doc_id_1")

app = Flask(__name__)
swagger = Swagger(app)

palette_mediator = view_mediator.ViewMediator(
    view_model_cls=PaletteViewModel,
    app=app,
)

palette_mediator.add_instance_get(rule="/palettes/<string:doc_id>")

if __name__ == "__main__":
    """
    Go to http://127.0.0.1:5000/apidocs/ for the auto-generated 
        documentations. 
    """

    from flask_boiler.config import Config
    from flask_boiler.context import Context as CTX

    if CTX.config is None:
        config = Config(
            app_name="flask-boiler-testing",
            debug=True,
            testing=True,
            certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
        )
        CTX.read(config)

    app.run(debug=True)
    # Now visit "http://127.0.0.1:5000/palettes/doc_id_1" to get json


"""
Reserved for testing; Not part of the example 
"""
import pytest


def test_view_example():
    from flask_boiler.config import Config
    from flask_boiler.context import Context as CTX

    if CTX.config is None:
        config = Config(
            app_name="flask-boiler-testing",
            debug=True,
            testing=True,
            certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
        )
        CTX.read(config)

    assert app.test_client().get(
        "http://127.0.0.1:5000/palettes/doc_id_1"
    ).json == {
               "colors": [
                   {
                       "name": "cian",
                       "obj_type": "dict"
                   },
                   {
                       "name": "magenta",
                       "obj_type": "dict"
                   },
                   {
                       "name": "yellow",
                       "obj_type": "dict"
                   },
                   {
                       "name": "black",
                       "obj_type": "dict"
                   }
               ],
               "palette_name": "cmyk"
           }
