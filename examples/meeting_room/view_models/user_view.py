from examples.meeting_room.domain_models.user import User
from examples.meeting_room.domain_models.meeting import Meeting
from examples.meeting_room.view_models import MeetingSession
from flask_boiler import fields, schema, view_model, view, attrs
from flask_boiler.business_property_store import BPSchema
from flask_boiler.struct import Struct


class UserBpss(BPSchema):
    user = fields.StructuralRef(dm_cls=User)

class UserViewMixin:

    first_name = attrs.bproperty(import_enabled=False)
    last_name = attrs.bproperty(import_enabled=False)
    organization = attrs.bproperty(import_enabled=False)

    hearing_aid_requested = attrs.bproperty(import_enabled=False)
    meetings = attrs.bproperty(import_enabled=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new(cls, doc_id=None):
        return cls.get_from_user_id(user_id=doc_id)

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

    @meetings.getter
    def meetings(self):
        meetings_generator = Meeting.where(users=("array_contains", self.store.user.doc_ref))
        return [
            MeetingSession.new(meeting=meeting).to_dict()
            for meeting in meetings_generator
        ]

    @classmethod
    def get_from_user_id(cls, user_id, once=False, **kwargs):
        struct = Struct(schema_obj=UserBpss())

        u: User = User.get(doc_id=user_id)

        struct["user"] = (User, u.doc_ref.id)

        return super().get(struct_d=struct, once=once, **kwargs)


class UserView(UserViewMixin, view_model.ViewModel):
    pass
