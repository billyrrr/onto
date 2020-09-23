import pytest
from flasgger import Swagger
from flask import Flask


@pytest.fixture
def CTX():
    """
    Note that pytest.fixture(scope="package") is experimental according
        to pytest documentations
    :return:
    """

    from onto.context import Context as TST_CTX
    from onto.config import Config

    if TST_CTX.config is None:
        config = Config.load()
        TST_CTX.read(config)

    return TST_CTX

@pytest.fixture
def setup_app(CTX):

    app = Flask(__name__)
    swagger = Swagger(app)

    return app
