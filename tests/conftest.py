import pytest

from tests.utils import _delete_all

def pytest_sessionstart(session):
    from flask_boiler.context import Context as CTX
    from flask_boiler.config import Config

    if CTX.config is None:
        config = Config(
            app_name="flask-boiler-testing",
            debug=True,
            testing=True,
            certificate_filename="flask-boiler-testing-firebase-adminsdk-4m0ec-7505aaef8d.json"
        )
        CTX.read(config)

    _delete_all(CTX, "Orbit")
    _delete_all(CTX, "locations")
    _delete_all(CTX, "orbits")
    _delete_all(CTX, "rideHosts")
    _delete_all(CTX, "riderBookings")
    _delete_all(CTX, "riderTargets")
    _delete_all(CTX, "users")

    _delete_all(CTX, "RainbowDAV")
    _delete_all(CTX, "Shard")
    _delete_all(CTX, "UserViewDAV")
    _delete_all(CTX, "categories")
    _delete_all(CTX, "counters")
    _delete_all(CTX, "hellos")


def pytest_sessionfinish(session, exitstatus):
    from flask_boiler.context import Context as CTX

    if exitstatus == 0:
        _delete_all(CTX, "Orbit")
        _delete_all(CTX, "locations")
        _delete_all(CTX, "orbits")
        _delete_all(CTX, "rideHosts")
        _delete_all(CTX, "riderBookings")
        _delete_all(CTX, "riderTargets")
        _delete_all(CTX, "users")

        _delete_all(CTX, "RainbowDAV")
        _delete_all(CTX, "Shard")
        _delete_all(CTX, "UserViewDAV")
        _delete_all(CTX, "categories")
        _delete_all(CTX, "counters")
        _delete_all(CTX, "hellos")
