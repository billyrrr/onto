import time

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models import UserView
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMutation, MeetingSessionMixin
from flask_boiler.view import DocumentAsView
from flask_boiler.view_mediator_dav import ViewMediatorDAV
from ..views import meeting_session_ops
from flask_boiler import view_mediator
# Import the fixtures used by fixtures
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location, meeting
from flask_boiler.context import Context


class MeetingSessionDAV(MeetingSessionMixin, DocumentAsView):

    @classmethod
    def new(cls, *args, **kwargs):
        return cls.get_from_meeting_id(*args, **kwargs)

    @classmethod
    def get_from_meeting_id(cls, meeting_id, once=False, user=None):
        doc_ref = user.doc_ref.collection(cls.__name__).document(meeting_id)
        return super().get_from_meeting_id(
            meeting_id, once=once, doc_ref=doc_ref)


class MeetingSessionViewMediatorDAV(ViewMediatorDAV):

    def __init__(self, *args, meeting_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_cls = meeting_cls

    def start(self):
        self.generate_entries()

    def generate_entries(self):

        meetings = self.meeting_cls.all()
        for meeting in meetings:
            assert isinstance(meeting, Meeting)
            for user_ref in meeting.users:
                user = User.get(doc_ref=user_ref)
                obj = self.view_model_cls.new(
                    meeting_id=meeting.doc_id,
                    once=False,
                    user=user
                )
                self.instances[(meeting.doc_id, user.doc_id)] = obj


def test_start(users, tickets, location, meeting):
    mediator = MeetingSessionViewMediatorDAV(
        view_model_cls=MeetingSessionDAV,
        meeting_cls=Meeting,
    )

    mediator.start()

    time.sleep(5)

    ref = Context.db.collection("users").document(users[0].doc_id) \
        .collection(MeetingSessionDAV.__name__).document(meeting.doc_id)
    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'obj_type': 'MeetingSessionDAV',
                                   'numHearingAidRequested': 2, 'doc_id': '',
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
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id)\
            .delete()


def test_domain_model_changes(users, tickets, location, meeting):
    """ Tests that view model updates when domain model is changed

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    mediator = MeetingSessionViewMediatorDAV(
        view_model_cls=MeetingSessionDAV,
        meeting_cls=Meeting,
    )

    mediator.start()

    time.sleep(5)

    ref = Context.db.collection("users").document(users[0].doc_id) \
        .collection(MeetingSessionDAV.__name__).document(meeting.doc_id)

    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'obj_type': 'MeetingSessionDAV',
                                   'numHearingAidRequested': 2, 'doc_id': '',
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

    # User Tijuana Furlong sets their attendance to False
    tickets[0].attendance = False
    tickets[0].save()

    time.sleep(3)

    """
    Expect the document to be updated to exclude Tijuana Furlong from a
      list of people attending the meeting session and the hearing aid
      counter.
    """
    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'obj_type': 'MeetingSessionDAV',
                                   'numHearingAidRequested': 1, 'doc_id': '',
                                   'attending': [
                                       {
                                           'name': 'Joshua Pendergrast',
                                           'organization': 'SDSU',
                                           'hearing_aid_requested': True},
                                       {
                                           'name': 'Thomasina Manes',
                                           'organization': 'UCSD',
                                           'hearing_aid_requested': False}
                                   ],
                                   'longitude': -117.242929,
                                   'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    for user in users:
        Context.db.collection("users").document(user.doc_id) \
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id)\
            .delete()


def test_view_model(users, tickets, location, meeting):
    meeting_session = MeetingSessionDAV \
        .get_from_meeting_id(meeting_id=meeting.doc_id,
                             once=True,
                             user=users[0])

    assert meeting_session._export_as_view_dict() == \
           {'inSession': True,
            'longitude': -117.242929,
            'latitude': 32.880361,
            'address': '9500 Gilman Drive, La Jolla, CA',
            'attending': [
                {
                    'name': 'Joshua Pendergrast',
                    'organization': 'SDSU',
                    'hearing_aid_requested': True},
                {
                    'name': 'Thomasina Manes',
                    'organization': 'UCSD',
                    'hearing_aid_requested': False},
                {
                    'name': 'Tijuana Furlong',
                    'organization': 'UCSD',
                    'hearing_aid_requested': True},
            ],
            'numHearingAidRequested': 2}
