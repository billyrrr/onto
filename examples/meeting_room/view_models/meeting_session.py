from examples.meeting_room.domain_models import Ticket, User
from examples.meeting_room.domain_models.location import Location
from examples.meeting_room.domain_models.meeting import Meeting
from onto import view_model, attrs
from onto.view.mutation import PatchMutation
from onto.store import Store, reference


class MeetingSessionStore(Store):
    tickets = reference(dm_cls=Ticket, many=True)
    users = reference(dm_cls=User, many=True)
    meeting = reference(dm_cls=Meeting)
    location = reference(dm_cls=Location)


class MeetingSessionMixin:

    class Meta:
        exclude = ('obj_type',)

    latitude = attrs.bproperty(import_enabled=False)
    longitude = attrs.bproperty(import_enabled=False)
    address = attrs.bproperty(import_enabled=False)
    attending = attrs.bproperty(import_enabled=False)
    in_session = attrs.bproperty(import_enabled=False)
    num_hearing_aid_requested = attrs.bproperty(import_enabled=False)

    # @num_hearing_aid_requested.create_accumulator
    # def num_hearing_aid_request(self, value=_NA):
    #     if value is _NA:
    #         return attrs.aggregation.Accumulator(value=0)
    #     else:
    #         return attrs.aggregation.Accumulator(value=value)

    # @num_hearing_aid_requested.getter
    # def num_hearing_aid_requested(self):
    #     res = 0
    #     for user in self.store.users:
    #         if user.hearing_aid_requested:
    #             res += 1
    #     return res

    @property
    def meeting_id(self):
        return self.store.meeting.doc_id

    @property
    def _view_refs(self):
        for user_id, user in self.store.users.items():
            doc_ref = user.doc_ref / self.__class__.__name__ / self.store.meeting.doc_id
            yield doc_ref

    @in_session.getter
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

    @latitude.getter
    def latitude(self):
        return self.store.location.latitude

    @longitude.getter
    def longitude(self):
        return self.store.location.longitude

    @address.getter
    def address(self):
        return self.store.location.address

    @attending.getter
    def attending(self):
        user_ids = [uid for uid in self.store.users.keys()]

        if self.store.meeting.status == "not-started":
            return list()

        res = list()
        for user_id in sorted(user_ids):
            ticket = self.store.tickets[user_id]
            user = self.store.users[user_id]
            if ticket.attendance:
                d = {
                    "name": user.display_name,
                    "organization": user.organization,
                    "hearing_aid_requested": user.hearing_aid_requested
                }
                res.append(d)

        return res

    @num_hearing_aid_requested.getter
    def num_hearing_aid_requested(self):
        count = 0
        for d in self.attending:
            if d["hearing_aid_requested"]:
                count += 1
        return count

    # @classmethod
    # def get_many_from_query(cls, query_d=None, once=False):
    #     """ Note that once kwarg apply to the snapshot but not the query.
    #
    #     :param query_d:
    #     :param once: attaches a listener to individual snapshots
    #     :return:
    #     """
    #     return [
    #         cls.get_from_meeting_id(meeting_id=obj.doc_id, once=once)
    #         for obj in Meeting.where(**query_d)]

    @classmethod
    def get(cls, doc_id=None, once=True, meeting=None, **kwargs):

        if meeting is None:
            m: Meeting = Meeting.get(doc_id=doc_id)
        else:
            m = meeting

        struct = dict()

        struct["meeting"] = (Meeting, m.doc_id)

        struct['users'] = dict()
        for user_ref in m.users:
            obj_type = User
            user_id = user_ref.id
            struct["users"][user_id] = (obj_type, user_ref.id)

        struct['tickets'] = dict()
        for user_id, ticket_ref in m.tickets.items():
            obj_type = Ticket
            struct["tickets"][user_id] = (obj_type, ticket_ref.id)

        struct["location"] = (Location, m.location.id)

        store = MeetingSessionStore.from_struct(struct)

        obj = super().get(store=store, once=once,
                          **kwargs)  # TODO: fix super() behavior
        # time.sleep(2)  # TODO: delete after implementing sync

        return obj

    @classmethod
    def get_many_from_query(cls, query_d=None, once=False):
        """ Note that once kwarg apply to the snapshot but not the query.

        :param query_d:
        :param once: attaches a listener to individual snapshots
        :return:
        """
        return [
            cls.get(doc_id=obj.doc_id, once=once)
            for obj in Meeting.where(**query_d)]

    def propagate_change(self):
        self.store.propagate_back()

    # def update_vals(self, *args, user_id, **kwargs):
    #     if user_id in self.store.users:
    #         super().update_vals(*args, **kwargs)
    #     else:
    #         raise UnauthorizedError


class MeetingSessionC(MeetingSessionMixin, view_model.ViewModelR):

    class Meta:
        collection_name = 'meeting_sessions'


class MeetingSession(MeetingSessionMixin, view_model.ViewModel):

    pass


class MeetingSessionMutation(PatchMutation):

    view_model_cls = MeetingSession
