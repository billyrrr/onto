"""

Contains test cases inspired by flasgger (MIT licence)
See: https://github.com/flasgger/flasgger/blob/master/LICENSE
"""
from onto import attrs
from flask import Flask
from flasgger import Swagger

from onto.models.base import Serializable
from onto.view import rest_api
from onto.view_model import ViewModel


repo = {

    "doc_id_1": dict(palette_name='cmyk',
                     colors=[
                         {'name': 'cian'},
                         {'name': 'magenta'},
                         {'name': 'yellow'},
                         {'name': 'black'}
                     ], )
}


class ExampleColor(Serializable):
    name = attrs.string()


class ExamplePaletteViewModel(ViewModel):

    class Meta:
        case_conversion = False

    palette_name = attrs.string()
    colors = attrs.embed(obj_cls=ExampleColor, many=True)

    description = "A list of colors (may be filtered by palette)"

    @classmethod
    def get(cls, *args, doc_id, once=True, **kwargs):
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


# obj = ExamplePaletteViewModel.new(doc_id="doc_id_1")

app = Flask(__name__)
swagger = Swagger(app)

palette_mediator = rest_api.ViewMediator(
    view_model_cls=ExamplePaletteViewModel,
    app=app,
)

palette_mediator.add_instance_get(rule="/palettes/<string:doc_id>")

if __name__ == "__main__":
    """
    Go to http://127.0.0.1:5000/apidocs/ for the auto-generated 
        documentations. 
    """

    from onto.config import Config
    from onto.context import Context as CTX

    if not CTX._ready:
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


def test_view_example():
    from onto.config import Config
    from onto.context import Context as CTX

    if not CTX._ready:
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
