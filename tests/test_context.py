import pytest


@pytest.mark.skip(reason='Context should be initialized with conftest already')
def test_firebase_app_context():
    from onto import config
    from onto import context

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


@pytest.mark.skip(reason='Context should be initialized with conftest already')
def test_context_load():
    from onto.context import Context as CTX

    CTX.load()

    assert CTX.firebase_app.project_id == "flask-boiler-testing"


def test_config_comparator():
    from onto.config import Config
    config = Config.load()
    other_config = Config.load()
    assert config == other_config


def test_errors(monkeypatch):
    # Note: Watch out for state sharing
    # Note: Context may have invalid values when used in other test cases
    from onto.context import Context

    class CertFailError(Exception):
        pass

    def initialize_cert_fail(*args, **kwargs):
        raise CertFailError

    with monkeypatch.context() as m:
        import firebase_admin
        m.setattr(firebase_admin.credentials, "Certificate", initialize_cert_fail)
        with pytest.raises(CertFailError):
            Context._reload_credentials('./non-existent.json')

    # class AppFailError(Exception):
    #     pass
    #
    # def initialize_app_fail(*args, **kwargs):
    #     raise AppFailError
    #
    # with monkeypatch.context() as m:
    #     import firebase_admin
    #     m.setattr(firebase_admin, "initialize_app", initialize_app_fail)
    #     _PartialConfig = type(
    #         "_PartialConfig",
    #         (object,),
    #         {"APP_NAME": "AppNameFail"}
    #     )
    #     m.setattr(Context, "config", _PartialConfig())
    #     with pytest.raises(AppFailError):
    #         Context._reload_firebase_app()

    with pytest.raises(Exception):
        Context._reload_credentials(certificate_path="non-existent")
