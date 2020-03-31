import pytest


def test_firebase_app_context():
    from flask_boiler import config
    from flask_boiler import context

    Config = config.Config

    config = Config(
        app_name="flask-boiler-testing",
        debug=True,
        testing=True,
        certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
    )
    CTX = context.Context
    CTX.read(config)
    assert CTX.firebase_app.project_id == "flask-boiler-testing"


def test_context_load():
    from flask_boiler.context import Context as CTX

    CTX.load()

    assert CTX.firebase_app.project_id == "flask-boiler-testing"


def test_config_comparator():
    from flask_boiler.config import Config
    config = Config.load()
    other_config = Config.load()
    assert config == other_config
