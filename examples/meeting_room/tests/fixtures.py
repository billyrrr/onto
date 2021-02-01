import pytest

from examples.meeting_room import domain_models


@pytest.fixture
def users(request, CTX):
    tijuana = domain_models.User.new(doc_id="tijuana")
    tijuana.first_name = "Tijuana"
    tijuana.last_name = "Furlong"
    tijuana.hearing_aid_requested = True
    tijuana.organization = "UCSD"
    print(tijuana.to_dict())
    tijuana.save()

    thomasina = domain_models.User.new(doc_id="thomasina")
    thomasina.first_name = "Thomasina"
    thomasina.last_name = "Manes"
    thomasina.hearing_aid_requested = False
    thomasina.organization = "UCSD"
    thomasina.save()

    joshua = domain_models.User.new(doc_id="joshua")
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
def tickets(users, request, CTX):
    tj_t = domain_models.Ticket.new(doc_id="tj_t")
    tj_t.role = "Participant"
    tj_t.user = domain_models.User._get_collection().child("tijuana")
    tj_t.attendance = True
    tj_t.save()

    ts_t = domain_models.Ticket.new(doc_id="ts_t")
    ts_t.role = "Organizer"
    ts_t.user = domain_models.User._get_collection().child("thomasina")
    ts_t.attendance = True
    ts_t.save()

    js_t = domain_models.Ticket.new(doc_id="js_t")
    js_t.role = "Participant"
    js_t.user = domain_models.User._get_collection().child("joshua")
    js_t.attendance = True
    js_t.save()

    def fin():
        tj_t.delete()
        ts_t.delete()
        js_t.delete()

    request.addfinalizer(fin)

    return [tj_t, ts_t, js_t]


@pytest.fixture
def location(request, CTX):
    obj = domain_models.Location.new()
    obj.latitude = 32.880361
    obj.longitude = -117.242929
    obj.address = "9500 Gilman Drive, La Jolla, CA"

    obj.save()

    def fin():
        obj.delete()

    request.addfinalizer(fin)

    return obj


@pytest.fixture
def meeting(users, tickets, location, request, CTX):
    m = domain_models.Meeting.new(doc_id="meeting_1")
    m.users = [user.doc_ref for user in users]
    m.tickets = {ticket.user.id: ticket.doc_ref for ticket in tickets}
    m.location = location.doc_ref
    m.status = "in-session"
    m.save()

    def fin():
        m.delete()

    request.addfinalizer(fin)

    return m
