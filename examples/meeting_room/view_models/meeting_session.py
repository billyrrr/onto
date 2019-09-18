from examples.meeting_room.domain_models.location import Location
from examples.meeting_room.domain_models.meeting import Meeting
from flask_boiler import fields, schema, view_model, view


class MeetingSessionSchema(schema.Schema):
    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()
    attending = fields.List()
    in_session = fields.Raw()
    num_hearing_aid_requested = fields.Raw()


class MeetingSession(view.FlaskAsViewMixin, view_model.ViewModel):

    _schema_cls = MeetingSessionSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = dict()
        self.tickets = dict()
        self.meeting = None
        self.location = None

    def set_user(self, user):
        self.users[user.doc_id] = user

    def set_ticket(self, ticket):
        self.tickets[ticket.user.id] = ticket

    def set_meeting(self, meeting):
        self.meeting = meeting

    def set_location(self, location):
        self.location = location

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
        for user_id in user_ids:
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

    @property
    def in_session(self):
        return self.meeting.status == "in_session"

    @classmethod
    def get_from_meeting_id(cls, meeting_id):
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

        return super().get(struct_d=struct)
