import time

import pytest

from .. import view_models
from .. import domain_models

from flask_boiler.context import Context as TST_CTX
from flask_boiler.config import Config

config = Config(
    app_name="gravitate-dive-testing",
    debug=True,
    testing=True,
    certificate_filename="gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json"
)
TST_CTX.read(config)


@pytest.fixture
def users(request):
    tijuana = domain_models.User.create(doc_id="tijuana")
    tijuana.first_name = "Tijuana"
    tijuana.last_name = "Furlong"
    tijuana.hearing_aid_requested = True
    tijuana.organization = "UCSD"
    tijuana.save()

    thomasina = domain_models.User.create(doc_id="thomasina")
    thomasina.first_name = "Thomasina"
    thomasina.last_name = "Manes"
    thomasina.hearing_aid_requested = False
    thomasina.organization = "UCSD"
    thomasina.save()

    joshua = domain_models.User.create(doc_id="joshua")
    joshua.first_name = "Joshua"
    joshua.last_name = "Pendergrast"
    joshua.hearing_aid_requested = True
    joshua.organization = "SDSU"
    joshua.save()

    def fin():
        tijuana.delete()
        thomasina.delete()
        joshua.delete()

    request.addfinalizer(fin)

    return [tijuana, thomasina, joshua]


@pytest.fixture
def tickets(users, request):
    tj_t = domain_models.Ticket.create(doc_id="tj_t")
    tj_t.role = "Participant"
    tj_t.user = domain_models.User._get_collection().document("tijuana")
    tj_t.attendance = True
    tj_t.save()

    ts_t = domain_models.Ticket.create(doc_id="ts_t")
    ts_t.role = "Organizer"
    ts_t.user = domain_models.User._get_collection().document("thomasina")
    ts_t.attendance = True
    ts_t.save()

    js_t = domain_models.Ticket.create(doc_id="js_t")
    js_t.role = "Participant"
    js_t.user = domain_models.User._get_collection().document("joshua")
    js_t.attendance = True
    js_t.save()

    def fin():
        tj_t.delete()
        ts_t.delete()
        js_t.delete()

    request.addfinalizer(fin)

    return [tj_t, ts_t, js_t]


@pytest.fixture
def location(request):
    obj = domain_models.Location.create()
    obj.latitude = 32.880361
    obj.longitude = -117.242929
    obj.address = "9500 Gilman Drive, La Jolla, CA"

    obj.save()

    def fin():
        obj.delete()

    request.addfinalizer(fin)

    return obj


@pytest.fixture
def meeting(users, tickets, location, request):
    m = domain_models.Meeting.create(doc_id="meeting_1")
    m.users = [user.doc_ref for user in users]
    m.tickets = [ticket.doc_ref for ticket in tickets]
    m.location = location.doc_ref
    m.status = "in-session"

    m.save()

    def fin():
        m.delete()

    request.addfinalizer(fin)

    return m


def test_view_model(users, tickets, location, meeting):
    meeting_session = view_models.MeetingSession \
        .get_from_meeting_id(meeting_id=meeting.doc_id, once=True)

    time.sleep(2)

    assert meeting_session._export_as_view_dict() == {'inSession': True,
                                               'longitude': -117.242929,
                                               'latitude': 32.880361,
                                               'address': '9500 Gilman Drive, La Jolla, CA',
                                               'attending': [
                                                   {
                                                   'name': 'Joshua Pendergrast',
                                                           'organization': 'SDSU',
                                                    'hearing_aid_requested': True},
                                                   {'name': 'Thomasina Manes',
                                                    'organization': 'UCSD',
                                                    'hearing_aid_requested': False},
                                                   {'name': 'Tijuana Furlong',
                                                    'organization': 'UCSD',
                                                    'hearing_aid_requested': True},
                                                   ],
                                               'numHearingAidRequested': 2}


def test_view_model_update(users, tickets, location, meeting):

    meeting_session = view_models.MeetingSession \
        .get_from_meeting_id(meeting_id=meeting.doc_id, once=False)

    time.sleep(2)

    tickets[0].attendance = False
    tickets[0].save()

    time.sleep(5)

    assert meeting_session._export_as_view_dict() == {'inSession': True,
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
