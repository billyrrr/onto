from examples.meeting_room.tests.test_view_model import *
from examples.meeting_room.tests.test_dav import *
from examples.view_example import test_view_example
from examples.distributed_counter_example import *

from .fixtures import CTX


def test_quickstart_example():
    from importlib import import_module
    _ = import_module("examples.quickstart_example")


def test_relationship_example():
    from importlib import import_module
    _ = import_module("examples.relationship_example")


def test_meeting_quickstart():
    from importlib import import_module
    _ = import_module("examples.meeting_room.quickstart")
