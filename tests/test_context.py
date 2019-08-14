from src import config
from src import context


Config = config.Config

def test_firebase_app_context():
    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )
    CTX = context.Context
    CTX.read(config)
    assert CTX.firebase_app.project_id == "gravitate-dive-testing"
