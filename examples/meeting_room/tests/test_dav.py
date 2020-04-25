import time

import pytest
from google.cloud.firestore_v1 import Watch, DocumentSnapshot, \
    DocumentReference, Query, CollectionReference

from examples.meeting_room.domain_models import Meeting, User
from examples.meeting_room.view_models import UserView
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMutation, MeetingSessionMixin
from examples.meeting_room.view_models.user_view import UserViewMixin
from flask_boiler.errors import UnauthorizedError
from flask_boiler.mutation import Mutation, PatchMutation
from flask_boiler.view_mediator_dav import ViewMediatorDAV, ProtocolBase, \
    ViewMediatorDeltaDAV
from flask_boiler.view_model import ViewModel
from ..views import meeting_session_ops
from flask_boiler import view_mediator, utils, testing_utils
# Import the fixtures used by fixtures
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location, meeting
from flask_boiler.context import Context


class MeetingSessionDAV(MeetingSessionMixin, ViewModel):

    @classmethod
    def new(cls, *args, **kwargs):
        return cls.get_from_meeting_id(*args, **kwargs)

    @classmethod
    def get_from_meeting_id(cls, meeting_id, once=True, **kwargs):
        return super().get_from_meeting_id(
            meeting_id, once=once, **kwargs)

    def save(self, *args, **kwargs):
        for user_id, user in self.store.users.items():
            doc_ref = user.doc_ref\
                .collection(self.__class__.__name__)\
                .document(self.store.meeting.doc_id)
            super().save(*args, doc_ref=doc_ref, **kwargs)

    def update_vals(self, *args, user_id, **kwargs):
        if user_id in self.store.users:
            super().update_vals(*args, **kwargs)
        else:
            raise UnauthorizedError


class MeetingSessionPatch(ViewMediatorDeltaDAV):

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            d = snapshot.to_dict()
            meeting_id = d["target_meeting_id"]

            d = {
                Meeting.get_schema_cls().g(key): val
                for key, val in d.items() if key in {"inSession"}
            }

            ref = snapshot.reference
            user_id = ref.parent.parent.id

            obj = MeetingSessionDAV.new(
                meeting_id=meeting_id,
                once=True,
            )
            obj.update_vals(user_id=user_id, with_dict=d)
            # TODO: switch to notify
            obj.propagate_change()


class MeetingSessionGet(ViewMediatorDeltaDAV):

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            meeting = utils.snapshot_to_obj(snapshot)

            assert isinstance(meeting, Meeting)

            obj = MeetingSessionDAV.new(
                meeting_id=meeting.doc_id,
                once=False,
                f_notify=mediator.notify
            )
            # mediator.notify(obj=obj)

        on_update = on_create


def test_start(users, tickets, location, meeting):
    mediator = MeetingSessionGet(query=
                                 Query(parent=Meeting._get_collection())
                                 )

    mediator.start()

    testing_utils._wait(factor=.7)

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
                                   # 'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    for user in users:
        Context.db.collection("users").document(user.doc_id) \
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id) \
            .delete()


def test_mutate(users, tickets, location, meeting):
    """
    Tests that mutate actions affect domain model and view model.

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    mediator = MeetingSessionGet(
        query=Query(parent=Meeting._get_collection())
    )

    mediator.start()

    testing_utils._wait(factor=.7)

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
                                   # 'doc_ref': 'users/tijuana/MeetingSessionDAV/meeting_1',
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    patch_collection_name = "{}_PATCH".format(MeetingSessionDAV.__name__)

    patch_mediator = MeetingSessionPatch(
        query=Context.db.collection_group(patch_collection_name)
    )

    patch_mediator.start()

    ref: CollectionReference = Context.db.collection(
        'users/tijuana/MeetingSessionDAV_PATCH'
    )
    ref.add(
        dict(
            target_meeting_id="meeting_1",
            inSession=False
        )
    )

    testing_utils._wait(factor=.7)

    m = Meeting.get(doc_id="meeting_1")
    assert m.status == "closed"

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
                                   'inSession': False,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}


    for user in users:
        Context.db.collection("users").document(user.doc_id) \
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id) \
            .delete()


def test_domain_model_changes(users, tickets, location, meeting):
    """ Tests that view model updates when domain model is changed

    :param users:
    :param tickets:
    :param location:
    :param meeting:
    :return:
    """
    mediator = MeetingSessionGet(
        query=Query(parent=Meeting._get_collection())
    )

    mediator.start()

    testing_utils._wait(factor=2)
    #
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
                                   'inSession': True,
                                   'address': '9500 Gilman Drive, La Jolla, CA'}

    # User Tijuana Furlong sets their attendance to False
    tickets[0].attendance = False
    tickets[0].save()

    testing_utils._wait(factor=.7)
    #
    """
    Expect the document to be updated to exclude Tijuana Furlong from a
      list of people attending the meeting session and the hearing aid
      counter.
    """
    assert ref.get().to_dict() == {'latitude': 32.880361,
                                   'obj_type': 'MeetingSessionDAV',
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
            .collection(MeetingSessionDAV.__name__).document(meeting.doc_id) \
            .delete()


def test_view_model(users, tickets, location, meeting):
    meeting_session = MeetingSessionDAV \
        .get_from_meeting_id(meeting_id=meeting.doc_id,
                             once=True)

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


class UserViewDAV(UserViewMixin, ViewModel):

    @classmethod
    def new(cls, *args, **kwargs):
        return cls.get_from_user_id(*args, **kwargs)

    @classmethod
    def get_from_user_id(cls, user_id, once=False, **kwargs):
        doc_ref = Context.db.collection(cls.__name__) \
            .document(user_id)
        return super().get_from_user_id(user_id, once=once, doc_ref=doc_ref,
                                        **kwargs)

    def propagate_change(self):
        self.store.user.save()


class UserViewMediatorDAV(ViewMediatorDAV):

    def __init__(self, *args, user_cls=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cls = user_cls

    @classmethod
    def notify(cls, obj):
        obj.save()

    def generate_entries(self):

        d = dict()
        users = self.user_cls.all()
        for user in users:
            assert isinstance(user, User)
            obj = self.view_model_cls.new(
                user_id=user.doc_id,
                once=False,
                f_notify=self.notify
            )
            d[obj.doc_ref._document_path] = obj
        return d


def test_user_view(users, tickets, location, meeting):
    user_view = UserViewDAV.new(user_id="thomasina", )
    user_view.wait_for_first_success()
    # time.sleep(3)  # TODO: delete after implementing sync

    assert user_view._export_as_view_dict() == {'meetings': [
        {'status': 'in-session', 'users': [
            {'lastName': 'Furlong', 'firstName': 'Tijuana',
             'hearingAidRequested': True, 'organization': 'UCSD'},
            {'lastName': 'Manes', 'firstName': 'Thomasina',
             'hearingAidRequested': False, 'organization': 'UCSD'},
            {'lastName': 'Pendergrast', 'firstName': 'Joshua',
             'hearingAidRequested': True, 'organization': 'SDSU'}],
         'location': {'latitude': 32.880361,
                      'address': '9500 Gilman Drive, La Jolla, CA',
                      'longitude': -117.242929},
         'tickets': [
             {'attendance': True, 'role': 'Participant',
              'user': {'lastName': 'Furlong', 'firstName': 'Tijuana',
                       'hearingAidRequested': True, 'organization': 'UCSD'}},
             {'attendance': True, 'role': 'Organizer',
              'user': {'lastName': 'Manes', 'firstName': 'Thomasina',
                       'hearingAidRequested': False, 'organization': 'UCSD'}},
             {'attendance': True, 'role': 'Participant',
              'user': {'lastName': 'Pendergrast', 'firstName': 'Joshua',
                       'hearingAidRequested': True,
                       'organization': 'SDSU'}}]}],
        'lastName': 'Manes',
        'firstName': 'Thomasina',
        'hearingAidRequested': False,
        'organization': 'UCSD'}


@pytest.mark.skip
def test_user_view_diff(users, tickets, location, meeting):
    user_view = UserViewDAV.new(user_id="thomasina", )

    # time.sleep(3)  # TODO: delete after implementing sync

    updated_dict = user_view._export_as_view_dict().copy()
    updated_dict["lastName"] = 'M.'

    res = user_view.diff(
        updated_dict
    )
    assert res == {'lastName': 'M.'}


def test_propagate_change(users, tickets, location, meeting):
    user_id = users[1].doc_id

    user_view = UserViewDAV.new(user_id=user_id, )
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
    user_view = mediator.instances[ref._document_path]

    ref.collection("_PATCH_UserViewDAV").add({
        "lastName": "Manes-Kennedy"
    })

    testing_utils._wait(factor=.7)

    updated_user = User.get(doc_id=user_id)

    assert updated_user.last_name == "Manes-Kennedy"

    res = user_view._export_as_view_dict()

    assert res['lastName'] == "Manes-Kennedy"
