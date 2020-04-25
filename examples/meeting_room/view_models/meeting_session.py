import time

from examples.meeting_room.domain_models import Ticket, User
from examples.meeting_room.domain_models.location import Location
from examples.meeting_room.domain_models.meeting import Meeting
from flask_boiler import fields, schema, view_model, view
from flask_boiler.business_property_store import BPSchema
from flask_boiler.mutation import Mutation, PatchMutation
from flask_boiler.struct import Struct
from flask_boiler.view_model import ViewModelMixin


class MeetingSessionSchema(schema.Schema):
    latitude = fields.Raw()
    longitude = fields.Raw()
    address = fields.Raw()
    attending = fields.List()
    in_session = fields.Raw()
    num_hearing_aid_requested = fields.Raw()


class MeetingSessionBpss(BPSchema):
    tickets = fields.StructuralRef(dm_cls=Ticket, many=True)
    users = fields.StructuralRef(dm_cls=User, many=True)
    meeting = fields.StructuralRef(dm_cls=Meeting)
    location = fields.StructuralRef(dm_cls=Location)


class MeetingSessionMixin:

    class Meta:
        schema_cls = MeetingSessionSchema

    def __init__(self, *args, meeting_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._meeting_id = meeting_id

    @property
    def _tickets(self):
        return {
            ticket.user.id: ticket
            for _, ticket in self.store.tickets.items()
        }

    @property
    def meeting_id(self):
        return self.store.meeting.doc_id

    @property
    def in_session(self):
        return self.store.meeting.status == "in-session"

    @in_session.setter
    def in_session(self, in_session):
        cur_status = self.store.meeting.status
        if cur_status == "in-session" and not in_session:
            self.store.meeting.status = "closed"
        elif cur_status == "closed" and in_session:
            self.store.meeting.status = "in-session"
        else:
            raise ValueError

    @property
    def latitude(self):
        return self.store.location.latitude

    @property
    def longitude(self):
        return self.store.location.longitude

    @property
    def address(self):
        return self.store.location.address

    @property
    def attending(self):
        user_ids = [uid for uid in self.store.users.keys()]

        if self.store.meeting.status == "not-started":
            return list()

        res = list()
        for user_id in sorted(user_ids):
            ticket = self._tickets[user_id]
            user = self.store.users[user_id]
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
        struct = Struct(schema_obj=MeetingSessionBpss())

        m: Meeting = Meeting.get(doc_id=meeting_id)

        struct["meeting"] = (Meeting, m.doc_ref.id)

        for user_ref in m.users:
            obj_type = User
            doc_id = user_ref.id
            struct["users"][doc_id] = (obj_type, user_ref.id)

        for ticket_ref in m.tickets:
            obj_type = Ticket
            doc_id = ticket_ref.id
            struct["tickets"][doc_id] = (obj_type, ticket_ref.id)

        struct["location"] = (Location, m.location.id)

        obj = cls.get(struct_d=struct, once=once,
                          meeting_id=m.doc_ref.id,
                          **kwargs)
        # time.sleep(2)  # TODO: delete after implementing sync

        return obj

    def propagate_change(self):
        self.store.propagate_back()


class MeetingSession(MeetingSessionMixin, view_model.ViewModel):
    pass


class MeetingSessionMutation(PatchMutation):

    view_model_cls = MeetingSession
