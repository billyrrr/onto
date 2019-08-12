import pytest
from testfixtures import compare

from src import schema, fields
from src.context import Context as CTX
from src.config import Config


def test_firebase_app_context():
    config = Config(
        app_name="gravitate-dive-testing",
        debug = True,
        testing = True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )
    CTX.read(config)
    assert CTX.firebase_app.project_id == "gravitate-dive-testing"
