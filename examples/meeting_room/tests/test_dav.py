import pytest
from google.cloud.firestore_v1 import CollectionReference

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models.meeting_session import MeetingSession
from examples.meeting_room.view_models.user_view import UserViewMixin
from flask_boiler.database import Reference, Snapshot
from flask_boiler.database.firestore import FirestoreReference
from flask_boiler.errors import UnauthorizedError
from flask_boiler.mutation import PatchMutation
from flask_boiler.query.query import Query, ViewModelQuery
from flask_boiler.source.firestore import FirestoreSource
from flask_boiler.view import Mediator
from flask_boiler.view.document import \
    ViewMediatorDAV
from flask_boiler.view.query_delta import ViewMediatorDeltaDAV, ProtocolBase
from flask_boiler.view_model import ViewModel
from flask_boiler import utils, testing_utils
# Import the fixtures used by fixtures
from flask_boiler.context import Context
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location, meeting
from flask_boiler import sink


class MeetingSessionPatch(Mediator):
    from flask_boiler.source.base import Source

    source = FirestoreSource(
        query=ViewModelQuery.patch_query(parent=MeetingSession)
    )
    sink = sink.firestore()

    @source.triggers.on_create
    def patch_meeting(self, reference, snapshot, transaction):
        d = snapshot.to_dict()
        meeting_id = d["target_meeting_id"]

        d = {
            Meeting.get_schema_cls().g(key): val
            for key, val in d.items() if key in {"inSession",}
        }

        ref = snapshot.reference
        user_id = ref.parent.parent.id

        obj = MeetingSession.get(
            doc_id=meeting_id,
            once=True,
        )
        obj.update_vals(user_id=user_id, with_dict=d)
        # TODO: switch to notify
        obj.propagate_change()


class MeetingSessionGet(Mediator):

    from flask_boiler import source

    source = source.domain_model(Meeting)
    sink = sink.firestore()

    @source.triggers.on_update
    @source.triggers.on_create
    def materialize_meeting_session(self, obj):
        meeting = obj
        assert isinstance(meeting, Meeting)

        def notify(obj):
            for ref in obj._view_refs:
                self.sink.emit(reference=ref, snapshot=obj.to_snapshot())

        _ = MeetingSession.get(
            doc_id=meeting.doc_id,
            once=False,
            f_notify=notify
        )
        # mediator.notify(obj=obj)

    @classmethod
    def start(cls):
        cls.source.start()


def test_start(users, tickets, location, meeting, CTX):

    MeetingSessionGet.start()

    testing_utils._wait()

    ref = Context.db.ref / "users" / users[0].doc_id / MeetingSession.__name__ / meeting.doc_id
    assert CTX.db.get(ref).to_dict() == {'latitude': 32.880361,
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
                                   # 'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    CTX.db.delete(ref=ref)


@pytest.fixture
def delete_after(request):
    def fin():
        patch_collection_name = "{}_PATCH".format(MeetingSession.__name__)
        for doc in Context.db.collection(
            f'users/tijuana/{patch_collection_name}'
        ).stream():
            doc.reference.delete()
    request.addfinalizer(finalizer=fin)


def test_mutate(users, tickets, location, meeting, delete_after, CTX):
    """
    Tests that mutate actions affect domain model and view model.

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    # mediator = MeetingSessionGet()
    # mediator.start()

    MeetingSessionPatch.start()

    testing_utils._wait(factor=.7)

    # testing_utils._wait(60)  # TODO: delete; used right now for breakpoint

    """
    Tests that MeetingSessionGet works 
    """
    ref = Context.db.ref/"users"/users[0].doc_id/MeetingSession.__name__/meeting.doc_id
    assert CTX.db.get(ref).to_dict() == {'latitude': 32.880361,
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
                                   # 'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    # testing_utils._wait(500)

    """
    Tests that MeetingSessionPatch works 
    """
    patch_ref = Context.db.ref/\
          f'users/tijuana/{ViewModelQuery.patch_query(parent=MeetingSession)}/patch_1'
    CTX.db.set(
        ref=patch_ref,
        snapshot=Snapshot(
            target_meeting_id="meeting_1",
            inSession=False
        )
    )

    testing_utils._wait(factor=.7)

    m = Meeting.get(doc_id="meeting_1")
    assert m.status == "closed"
    #
    # ref = Context.db.collection("users").document(users[0].doc_id) \
    #     .collection(MeetingSession.__name__).document(meeting.doc_id)
    assert CTX.db.get(ref=ref).to_dict() == {'latitude': 32.880361,
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
                                   'inSession': False,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    for user in users:
        reference = CTX.db.ref/"users"/user.doc_id/MeetingSession.__name__/meeting.doc_id
        CTX.db.delete(reference)


def test_domain_model_changes(users, tickets, location, meeting):
    """ Tests that view model updates when domain model is changed

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    mediator = MeetingSessionGet()

    mediator.start()

    testing_utils._wait(factor=2)

    ref = Context.db.collection("users").document(users[0].doc_id) \
        .collection(MeetingSession.__name__).document(meeting.doc_id)

    assert ref.get().to_dict() == {'latitude': 32.880361,
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
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    # User Tijuana Furlong sets their attendance to False
    tickets[0].attendance = False
    tickets[0].save()

    testing_utils._wait()

    """
    Expect the document to be updated to exclude Tijuana Furlong from a
      list of people attending the meeting session and the hearing aid
      counter.
    """
    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'numHearingAidRequested': 1,
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
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    for user in users:
        Context.db.collection("users").document(user.doc_id) \
            .collection(MeetingSession.__name__).document(meeting.doc_id) \
            .delete()


def test_view_model(users, tickets, location, meeting):
    meeting_session = MeetingSession.get(doc_id=meeting.doc_id,
                                         once=True)

    assert meeting_session.to_dict() == \
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


class UserViewDAV(UserViewMixin, ViewModel):

    @classmethod
    def get(cls, user_id, once=False, **kwargs):
        return super().get_from_user_id(user_id, once=once,
                                        **kwargs)

    def notify(self, obj):
        doc_ref = Context.db.document(f"UserViewDAV/{obj.user_id}")
        doc_ref.set(obj.to_dict())

    def propagate_change(self):
         self.store.user.save()


class UserViewMediatorDAV(ViewMediatorDAV):

    def __init__(self, *args, user_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cls = user_cls

    @classmethod
    def notify(cls, obj):
        doc_ref = Context.db.document(f"UserViewDAV/{obj.user_id}")
        doc_ref.set(obj.to_dict())

    def generate_entries(self):
        d = dict()
        users = self.user_cls.all()
        for user in users:
            assert isinstance(user, User)
            user_id = user.doc_id
            obj = self.view_model_cls.get(
                user_id=user_id,
                once=False,
                f_notify=self.notify
            )
            d[Context.db.document(f"UserViewDAV/{user_id}")._document_path] = obj
        return d


def test_user_view(users, tickets, location, meeting):
    user_view = UserViewDAV.get(user_id="thomasina", )
    user_view.wait_for_first_success()
    # time.sleep(3)  # TODO: delete after implementing sync

    assert user_view.to_dict() == {
        'firstName': 'Thomasina',
        'hearingAidRequested': False,
        'lastName': 'Manes',
        'meetings': [{'address': '9500 Gilman Drive, La Jolla, CA',
                      'attending': [{'hearing_aid_requested': True,
                                     'name': 'Joshua Pendergrast',
                                     'organization': 'SDSU'},
                                    {'hearing_aid_requested': False,
                                     'name': 'Thomasina Manes',
                                     'organization': 'UCSD'},
                                    {'hearing_aid_requested': True,
                                     'name': 'Tijuana Furlong',
                                     'organization': 'UCSD'}],
                      'inSession': True,
                      'latitude': 32.880361,
                      'longitude': -117.242929,
                      'numHearingAidRequested': 2}],
        'obj_type': 'UserViewDAV',
        'organization': 'UCSD'}


@pytest.mark.skip
def test_user_view_diff(users, tickets, location, meeting):
    user_view = UserViewDAV.get(user_id="thomasina", )

    # time.sleep(3)  # TODO: delete after implementing sync

    updated_dict = user_view._export_as_view_dict().copy()
    updated_dict["lastName"] = 'M.'

    res = user_view.diff(
        updated_dict
    )
    assert res == {'lastName': 'M.'}


def test_propagate_change(users, tickets, location, meeting):
    user_id = users[1].doc_id

    user_view = UserViewDAV.get(user_id=user_id, )
    user_view.wait_for_first_success()

    # time.sleep(3)

    user_view.store.user.last_name = "M."
    user_view.propagate_change()

    user_ref = Context.db.collection("users").document(user_id)
    assert user_ref.get().to_dict()["lastName"] == "M."


class UserViewMutationDAV(PatchMutation):
    pass


def test_mutation(users, tickets, location, meeting):
    user_id = users[1].doc_id

    mediator = UserViewMediatorDAV(
        view_model_cls=UserViewDAV,
        user_cls=User,
        mutation_cls=UserViewMutationDAV
    )

    mediator.start()

    ref = Context.db.collection("UserViewDAV").document(user_id)

    # time.sleep(3)  # TODO: delete after implementing sync
    #
    user_view = mediator.instances[Context.db.document(f"UserViewDAV/{user_id}")._document_path]

    ref.collection("_PATCH_UserViewDAV").add({
        "lastName": "Manes-Kennedy"
    })

    testing_utils._wait(factor=.7)

    updated_user = User.get(doc_id=user_id)

    assert updated_user.last_name == "Manes-Kennedy"

    res = user_view.to_dict()

    assert res['lastName'] == "Manes-Kennedy"
