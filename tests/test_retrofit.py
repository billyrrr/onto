import time

from flasgger import SwaggerView

from flask_boiler import retrofit
import pytest
from .fixtures import CTX


def test_retrofit(CTX):

    class ExampleView(SwaggerView):
        def get(self):
            return {"0": {
                "name": "Hello"
            }}

    retrofit._retrofit(view=ExampleView(), collection_path="hellos")

    time.sleep(5)
