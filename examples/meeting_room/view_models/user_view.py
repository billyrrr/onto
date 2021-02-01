from examples.meeting_room.domain_models.user import User
from examples.meeting_room.domain_models.meeting import Meeting
from examples.meeting_room.view_models import MeetingSession
from onto import view_model
from onto.attrs import attrs
from onto.context import Context as CTX
from onto.store import Store, reference


class UserStore(Store):
    user = reference(dm_cls=User)


class UserViewMixin:

    user_id: str = attrs.of_type(str).optional
    first_name = attrs.str.data_key('firstName')
    last_name = attrs.str.data_key('lastName')
    organization = attrs.str.data_key('organization')

    hearing_aid_requested = attrs.bool.data_key('hearingAidRequested')
    # meetings = attrs.bproperty(import_enabled=False)

    @first_name.getter
    def first_name(self):
        return self.store.user.first_name

    @last_name.getter
    def last_name(self):
        return self.store.user.last_name

    @last_name.setter
    def last_name(self, new_last_name):
        self.store.user.last_name = new_last_name

    @organization.getter
    def organization(self):
        return self.store.user.organization

    @hearing_aid_requested.getter
    def hearing_aid_requested(self):
        return self.store.user.hearing_aid_requested
    #
    # @meetings.getter
    # def meetings(self):
    #     meetings_generator = Meeting.where(
    #         users=("array_contains", str(self.store.user.doc_ref))
    #     )
    #     return [
    #         MeetingSession.get(meeting=meeting).to_dict()
    #         for meeting in meetings_generator
    #     ]

    @classmethod
    def get(cls, user_id, once=False, **kwargs):
        struct = dict()
        struct["user"] = (User, user_id)
        store = UserStore.from_struct(struct)
        return super().get(store=store, once=once, user_id=user_id,
                           **kwargs)

    get_from_user_id = get


class UserView(UserViewMixin, view_model.ViewModel):
    pass


class UserViewDAV(UserViewMixin, view_model.ViewModel):

    @property
    def doc_ref(self):
        doc_ref = CTX.db.ref/"UserViewDAV"/self.user_id
        return doc_ref
