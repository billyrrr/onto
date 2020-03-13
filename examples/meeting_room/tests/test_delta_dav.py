import time

import pytest
from google.cloud.firestore_v1 import Watch, DocumentSnapshot, \
    DocumentReference, Query

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models import UserView
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMutation, MeetingSessionMixin
from examples.meeting_room.view_models.user_view import UserViewMixin
from flask_boiler.mutation import Mutation, PatchMutation
from flask_boiler.view import DocumentAsView
from flask_boiler.view_mediator_dav import ViewMediatorDAV, \
    ViewMediatorDeltaDAV, ProtocolBase
from flask_boiler.view_model import ViewModel
from ..views import meeting_session_ops
from flask_boiler import view_mediator, utils
# Import the fixtures used by fixtures
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location, meeting
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


class MeetingSessionProtocol(ProtocolBase):

    @staticmethod
    def on_create(snapshot, mediator):
        meeting = utils.snapshot_to_obj(snapshot)

        assert isinstance(meeting, Meeting)
        for user_ref in meeting.users:
            user = User.get(doc_ref=user_ref)
            _ = MeetingSessionDAV.new(
                meeting_id=meeting.doc_id,
                once=False,
                user=user,
                f_notify=mediator.notify
            )


class MeetingSessionViewMediatorDeltaDAV(ViewMediatorDeltaDAV):

    Protocol = MeetingSessionProtocol


def test_start(users, tickets, location, meeting):
    mediator = MeetingSessionViewMediatorDeltaDAV(
        query=Query(parent=Meeting._get_collection()),
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


