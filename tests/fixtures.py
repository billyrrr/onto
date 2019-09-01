import pytest


@pytest.fixture(scope="package")
def CTX():
    """
    Note that pytest.fixture(scope="package") is experimental according
        to pytest documentations
    :return:
    """

    from src.context import Context as TST_CTX
    from src.config import Config

    config = Config(
        app_name="gravitate-dive-testing",
        debug=True,
        testing=True,
        certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
    )
    TST_CTX.read(config)
    return TST_CTX
