import time

from flasgger import SwaggerView

from onto import retrofit
import pytest
from .fixtures import CTX


@pytest.mark.skip
def test_retrofit(CTX):

    class ExampleView(SwaggerView):
        def get(self):
            return {"0": {
                "name": "Hello"
            }}

    retrofit._retrofit(view=ExampleView(), collection_path="hellos")

    # time.sleep(5)
