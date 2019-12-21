import time

from google.cloud.firestore_v1 import Query

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMixin
from flask_boiler.view import DocumentAsView
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
from firestore_odm import utils
# Import the fixtures used by fixtures
from flask_boiler.context import Context


class MeetingSessionDAV(MeetingSessionMixin, DocumentAsView):

    @classmethod
    def new(cls, *args, **kwargs):
        return cls.get_from_meeting_id(*args, **kwargs)

    @classmethod
    def get_from_meeting_id(cls, meeting_id, once=False, user=None, **kwargs):
        doc_ref = user.doc_ref.collection(cls.__name__).document(meeting_id)
        return super().get_from_meeting_id(
            meeting_id, once=once, doc_ref=doc_ref, **kwargs)


class MeetingSessionViewMediatorDeltaDAV(ViewMediatorDeltaDAV):

    def __init__(self, *args, meeting_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_cls = meeting_cls

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.meeting_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    assert issubclass(self.meeting_cls, Meeting)
                    meeting = utils.snapshot_to_obj(
                        snapshot,
                        super_cls=self.meeting_cls
                    )

                    assert isinstance(meeting, Meeting)
                    for user_ref in meeting.users:
                        user = User.get(doc_ref=user_ref)
                        obj = self.view_model_cls.new(
                            meeting_id=meeting.doc_id,
                            once=False,
                            user=user,
                            f_notify=self.notify
                        )

        return query, on_snapshot


def test_start(users, tickets, location, meeting):
    mediator = MeetingSessionViewMediatorDeltaDAV(
        view_model_cls=MeetingSessionDAV,
        meeting_cls=Meeting,
    )

    mediator.start()

    time.sleep(10)

    ref = Context.db.collection("users").document(users[0].doc_id) \
        .collection(MeetingSessionDAV.__name__).document(meeting.doc_id)
    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'obj_type': 'MeetingSessionDAV',
                                   'numHearingAidRequested': 2,
                                   'attending': [
                                       {'hearing_aid_requested': True,
                                        'name': 'Joshua Pendergrast',
                                        'organization': 'SDSU'},
                                       {'organization': 'UCSD',
                                        'hearing_aid_requested': False,
                                        'name': 'Thomasina Manes'},
                                       {'organization': 'UCSD',
                                        'hearing_aid_requested': True,
                                        'name': 'Tijuana Furlong'}],
                                   'longitude': -117.242929,
                                   'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    for user in users:
        Context.db.collection("users").document(user.doc_id) \
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id) \
            .delete()


