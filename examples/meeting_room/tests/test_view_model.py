import time

from examples.meeting_room.view_models import MeetingSession
from examples.meeting_room.view_models.meeting_session import \
    MeetingSessionMutation
from ..views import meeting_session_ops
from onto import testing_utils
from onto.view import rest_api
from .. import view_models
# Import the fixtures used by fixtures
from tests.fixtures import CTX, setup_app
from .fixtures import users, tickets, location, meeting


def test_view_model(users, tickets, location, meeting):
    meeting_session = view_models.MeetingSession \
        .get(doc_id=meeting.doc_id, once=True)

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


def test_view(users, tickets, location, meeting, setup_app):
    app = setup_app

    mediator = rest_api.ViewMediator(
        view_model_cls=MeetingSession,
        app=app,
        mutation_cls=MeetingSessionMutation
    )
    mediator.add_list_get(
        rule="/meeting_sessions",
        list_get_view=meeting_session_ops.ListGet
    )

    testing_utils._wait(factor=2)

    test_client = app.test_client()

    res = test_client.get(
        path='meeting_sessions?status=in-session')

    assert res.json == {'results': {
        "meeting_1": {'inSession': True,
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
    }
    }

    mediator.add_instance_get(rule="/meeting_sessions/<string:doc_id>")
    res = test_client.get(
        path='meeting_sessions/meeting_1')

    assert res.json == {'inSession': True,
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

    mediator.add_instance_patch(rule="/meeting_sessions/<string:doc_id>")
    test_client.patch(
        path='meeting_sessions/meeting_1', json={
            "inSession": False
        })

    testing_utils._wait(factor=.7)

    res = test_client.get(
        path='meeting_sessions/meeting_1')

    assert res.json == {'inSession': False,
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


def test_user_view(users, meeting):
    user_view = view_models.UserView.get_from_user_id(user_id="thomasina", )

    # time.sleep(2)  # TODO: delete after implementing sync

    assert user_view.to_dict() == {'meetings': [
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
         'tickets': {'joshua': {'attendance': True,
                                      'role': 'Participant',
                                      'user': {'firstName': 'Joshua',
                                               'hearingAidRequested': True,
                                               'lastName': 'Pendergrast',
                                               'organization': 'SDSU'}},
                           'thomasina': {'attendance': True,
                                         'role': 'Organizer',
                                         'user': {'firstName': 'Thomasina',
                                                  'hearingAidRequested': False,
                                                  'lastName': 'Manes',
                                                  'organization': 'UCSD'}},
                           'tijuana': {'attendance': True,
                                       'role': 'Participant',
                                       'user': {'firstName': 'Tijuana',
                                                'hearingAidRequested': True,
                                                'lastName': 'Furlong',
                                                'organization': 'UCSD'}}}}],
        'lastName': 'Manes',
        'firstName': 'Thomasina',
        'hearingAidRequested': False,
        'organization': 'UCSD'}


def test_view_model_update(users, tickets, location, meeting):
    meeting_session = view_models.MeetingSession \
        .get(doc_id=meeting.doc_id, once=False)

    # time.sleep(2)  # TODO: delete after implementing sync

    tickets[0].attendance = False
    tickets[0].save()

    testing_utils._wait()

    assert meeting_session.to_dict() == {'inSession': True,
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
                                                              'hearing_aid_requested': False}
                                                      ],
                                                      'numHearingAidRequested': 1}
