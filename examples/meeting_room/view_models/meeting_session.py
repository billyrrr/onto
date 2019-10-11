import time

from examples.meeting_room.domain_models.location import Location
from examples.meeting_room.domain_models.meeting import Meeting
from flask_boiler import fields, schema, view_model, view
from flask_boiler.mutation import Mutation


class MeetingSessionSchema(schema.Schema):
    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()
    attending = fields.List()
    in_session = fields.Raw()
    num_hearing_aid_requested = fields.Raw()


class MeetingSessionMixin:

    _schema_cls = MeetingSessionSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = dict()
        self.tickets = dict()
        self.meeting = None
        self.location = None

    @property
    def meeting_id(self):
        return self.meeting.doc_id

    def set_user(self, user):
        self.users[user.doc_id] = user

    def set_ticket(self, ticket):
        self.tickets[ticket.user.id] = ticket

    def set_meeting(self, meeting):
        self.meeting = meeting

    def set_location(self, location):
        self.location = location

    @property
    def in_session(self):
        return self.meeting.status == "in-session"

    @in_session.setter
    def in_session(self, in_session):
        cur_status = self.meeting.status
        if cur_status == "in-session" and not in_session:
            self.meeting.status = "closed"
        elif cur_status == "closed" and in_session:
            self.meeting.status = "in-session"
        else:
            raise ValueError

    @property
    def latitude(self):
        return self.location.latitude

    @property
    def longitude(self):
        return self.location.longitude

    @property
    def address(self):
        return self.location.address

    @property
    def attending(self):
        user_ids = [uid for uid in self.users.keys()]

        if self.meeting.status == "not-started":
            return list()

        res = list()
        for user_id in sorted(user_ids):
            ticket = self.tickets[user_id]
            user = self.users[user_id]
            if ticket.attendance:
                d = {
                    "name": user.display_name,
                    "organization": user.organization,
                    "hearing_aid_requested": user.hearing_aid_requested
                }
                res.append(d)

        return res

    @property
    def num_hearing_aid_requested(self):
        count = 0
        for d in self.attending:
            if d["hearing_aid_requested"]:
                count += 1
        return count

    @classmethod
    def get_many_from_query(cls, query_d=None, once=False):
        """ Note that once kwarg apply to the snapshot but not the query.

        :param query_d:
        :param once: attaches a listener to individual snapshots
        :return:
        """
        return [
            cls.get_from_meeting_id(meeting_id=obj.doc_id, once=once)
            for obj in Meeting.where(**query_d)]

    @classmethod
    def new(cls, doc_id=None):
        return cls.get_from_meeting_id(meeting_id=doc_id)

    @classmethod
    def get_from_meeting_id(cls, meeting_id, once=False, **kwargs):
        struct = dict()

        m: Meeting = Meeting.get(doc_id=meeting_id)

        def meeting_update_func(vm: MeetingSession, dm):
            vm.set_meeting(dm)
        struct[m.doc_id] = ("Meeting", m.doc_ref.id, meeting_update_func)

        for user_ref in m.users:
            obj_type = "User"
            doc_id = user_ref.id

            def update_func(vm: MeetingSession, dm):
                 vm.set_user(dm)

            struct[doc_id] = (obj_type, user_ref.id, update_func)

        for ticket_ref in m.tickets:
            obj_type = "Ticket"
            doc_id = ticket_ref.id

            def update_func(vm: MeetingSession, dm):
                 vm.set_ticket(dm)

            struct[doc_id] = (obj_type, ticket_ref.id, update_func)

        def location_update_func(vm: MeetingSession, dm):
            vm.set_location(dm)
        struct[m.location.id] = ("Location", m.location.id, location_update_func)

        obj = super().get(struct_d=struct, once=once, **kwargs)
        time.sleep(2)  # TODO: delete after implementing sync
        return obj

    def propagate_change(self):
        self.meeting.save()


class MeetingSession(MeetingSessionMixin, view.FlaskAsView):
    pass


class MeetingSessionMutation(Mutation):

    view_model_cls = MeetingSession
