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

    from firestore_odm.context import Context as TST_CTX
    from firestore_odm.config import Config

    config = Config(
        app_name="flask-boiler-testing",
        debug=True,
        testing=True,
        certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
    )
    TST_CTX.read(config)
    return TST_CTX


@pytest.fixture
def setup_app(CTX):

    app = Flask(__name__)
    swagger = Swagger(app)

    return app
