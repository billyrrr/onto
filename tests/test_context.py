from flask_boiler import config
from flask_boiler import context


Config = config.Config

def test_firebase_app_context():
    config = Config(
        app_name="flask-boiler-testing",
        debug=True,
        testing=True,
        certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
    )
    CTX = context.Context
    CTX.read(config)
    assert CTX.firebase_app.project_id == "flask-boiler-testing"
