from google.cloud.firestore import Increment

from examples.meeting_room.tests.test_view_model import *
from examples.meeting_room.tests.test_dav import *

from examples import distributed_counter_example as dc
from .fixtures import CTX


def test_start(CTX):
    """
    TODO: add teardown steps to delete documents generated in firestore

    :param CTX:
    :return:
    """

    mediator = dc.CounterMediator(
        mutation_cls=None,
        shard_size=2
    )

    mediator.start()

    time.sleep(3)

    doc_ref = CTX.db.collection("counters").document("counter_0")

    assert doc_ref.get().to_dict() == {
        "doc_ref": "counters/counter_0",
        "obj_type": "CounterView",
        "totalCount": 0
    }

    CTX.db.collection("Shard").document("0").set(
        document_data={
            "count": Increment(1),
        },
        merge=True
    )

    time.sleep(1)

    assert doc_ref.get().to_dict() == {
        "doc_ref": "counters/counter_0",
        "obj_type": "CounterView",
        "totalCount": 1
    }
