import pytest

# from tests.utils import _delete_all

def pytest_sessionstart(session):
    from onto.context import Context as CTX
    from onto.config import Config

    if CTX.config is None:
        config = Config.load()
        CTX.read(config)
    #
    # _delete_all(CTX, "Orbit")
    # _delete_all(CTX, "locations")
    # _delete_all(CTX, "orbits")
    # _delete_all(CTX, "rideHosts")
    # _delete_all(CTX, "riderBookings")
    # _delete_all(CTX, "riderTargets")
    # _delete_all(CTX, "users")
    #
    # _delete_all(CTX, "RainbowDAV")
    # _delete_all(CTX, "Shard")
    # _delete_all(CTX, "UserViewDAV")
    # _delete_all(CTX, "categories")
    # _delete_all(CTX, "counters")
    # _delete_all(CTX, "hellos")
    #
    # _delete_all(CTX, subcollection_name="MeetingSessionDAV_PATCH")
    # _delete_all(CTX, subcollection_name="_PATCH_UserViewDAV")
    # _delete_all(CTX, subcollection_name="MeetingSessionDAV")


def pytest_sessionfinish(session, exitstatus):
    from onto.context import Context as CTX
    #
    # if exitstatus == 0:
    #     _delete_all(CTX, "Orbit")
    #     _delete_all(CTX, "locations")
    #     _delete_all(CTX, "orbits")
    #     _delete_all(CTX, "rideHosts")
    #     _delete_all(CTX, "riderBookings")
    #     _delete_all(CTX, "riderTargets")
    #     _delete_all(CTX, "users")
    #
    #     _delete_all(CTX, "RainbowDAV")
    #     _delete_all(CTX, "Shard")
    #     _delete_all(CTX, "UserViewDAV")
    #     _delete_all(CTX, "categories")
    #     _delete_all(CTX, "counters")
    #     _delete_all(CTX, "hellos")
    #
    #     _delete_all(CTX, subcollection_name="MeetingSessionDAV_PATCH")
    #     _delete_all(CTX, subcollection_name="_PATCH_UserViewDAV")
    #     _delete_all(CTX, subcollection_name="MeetingSessionDAV")
