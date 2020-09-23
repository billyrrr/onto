import pytest

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models.meeting_session import MeetingSession
from onto.database import Snapshot
from onto.view.mutation import PatchMutation
from onto.query.query import ViewModelQuery
from onto.view.document import \
    ViewMediatorDAV
from onto import testing_utils
# Import the fixtures used by fixtures
from onto.context import Context
from tests.fixtures import CTX
from .fixtures import *
from examples.meeting_room.view_models.user_view import UserViewDAV


def test_start_flask(users, tickets, location, meeting, CTX):

    from examples.meeting_room.views.rest_mediators import MeetingSessionRest
    from flask import Flask
    app = Flask(__name__)
    MeetingSessionRest.start(app)

    testing_utils._wait()

    test_client = app.test_client()

    res = test_client.get(
        path='meeting_sessions/meeting_1')

    assert res.json.items() >= {'latitude': 32.880361,
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
                                   'address': '9500 Gilman Drive, La Jolla, CA'}.items()

    res = test_client.get(
        path='meeting_sessions/')
    assert res == dict()


def test_start(users, tickets, location, meeting, CTX):

    from examples.meeting_room.views.mediators import MeetingSessionShow
    MeetingSessionShow.start()

    testing_utils._wait()

    ref = Context.db.ref / "users" / users[0].doc_id / MeetingSession.__name__ / meeting.doc_id
    assert CTX.dbs.leancloud.get(ref).to_dict().items() >= {'latitude': 32.880361,
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
                                   'address': '9500 Gilman Drive, La Jolla, CA'}.items()

    CTX.db.delete(ref=ref)


def test_start_fs(users, tickets, location, meeting, CTX):

    from examples.meeting_room.views.mediators import MeetingSessionGet
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
def delete_after(request, CTX):
    def fin():
        patch_collection_name = "{}_PATCH".format(MeetingSession.__name__)
        col_ref = Context.db.ref/'**'/patch_collection_name
        q = ViewModelQuery(ref=col_ref)
        for ref, _ in CTX.db.query(q):
            CTX.db.delete(ref=ref)
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

    from examples.meeting_room.views.mediators import MeetingSessionGet
    from examples.meeting_room.views.mediators import MeetingSessionPatch
    MeetingSessionGet.start()
    MeetingSessionPatch.start()  # TODO: isolate state between tests

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
    patch_ref = Context.db.ref/'users'/'tijuana'/'MeetingSession_PATCH'/meeting.doc_id
    CTX.db.update(
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


def test_mutate_fs(users, tickets, location, meeting, delete_after, CTX):
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

    from examples.meeting_room.views.mediators import MeetingSessionGet
    from examples.meeting_room.views.mediators import MeetingSessionPatch
    MeetingSessionGet.start()
    MeetingSessionPatch.start()  # TODO: isolate state between tests

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
    patch_ref = Context.db.ref/'users'/'tijuana'/'MeetingSession_PATCH'/meeting.doc_id
    CTX.db.update(
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


@pytest.fixture
def delete_meeting_sessions(request, CTX):
    def fin():
        col_ref = Context.db.ref/'**'/MeetingSession.__name__
        q = ViewModelQuery(ref=col_ref)
        for ref, _ in CTX.db.query(q):
            CTX.db.delete(ref=ref)
    request.addfinalizer(finalizer=fin)


def test_domain_model_changes(users, tickets, location, meeting, delete_meeting_sessions, CTX):
    """ Tests that view model updates when domain model is changed
    The feature is currently broken; it requires an active connection for all
        models in store

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    from examples.meeting_room.views.mediators import MeetingSessionGet
    mediator = MeetingSessionGet()

    mediator.start()

    testing_utils._wait(factor=2)

    ref = Context.db.ref/"users"/users[0].doc_id/MeetingSession.__name__/meeting.doc_id

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
    assert CTX.db.get(ref=ref).to_dict()  == {'latitude': 32.880361,
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


def test_view_model(users, tickets, location, meeting, delete_meeting_sessions):
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


class UserViewMediatorDAV(ViewMediatorDAV):

    def __init__(self, *args, user_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cls = user_cls

    @classmethod
    def notify(cls, obj):
        doc_ref = CTX.db.ref/"UserViewDAV"/obj.user_id
        doc_ref.set(obj.to_dict())

    # def generate_entries(self):
    #     d = dict()
    #     users = self.user_cls.all()
    #     for user in users:
    #         assert isinstance(user, User)
    #         user_id = user.doc_id
    #         obj = self.view_model_cls.get(
    #             user_id=user_id,
    #             once=False,
    #             f_notify=self.notify
    #         )
    #         d[Context.db.document(f"UserViewDAV/{user_id}")._document_path] = obj
    #     return d


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


def test_propagate_change(users, tickets, location, meeting, CTX):
    user_id = users[1].doc_id

    user_view = UserViewDAV.get(user_id=user_id, )
    user_view.wait_for_first_success()

    # time.sleep(3)

    user_view.store.user.last_name = "M."
    user_view.propagate_change()

    user_ref = Context.db.ref/"users"/user_id
    assert CTX.db.get(ref=user_ref).to_dict()["lastName"] == "M."


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
