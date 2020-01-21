from examples.meeting_room.domain_models.user import User
from examples.meeting_room.domain_models.meeting import Meeting
from flask_boiler import fields, schema, view_model, view
from flask_boiler.business_property_store import BPSchema
from flask_boiler.struct import Struct


class UserViewSchema(schema.Schema):

    first_name = fields.Raw(dump_only=True)
    last_name = fields.Raw(dump_only=True)
    organization = fields.Raw(dump_only=True)

    hearing_aid_requested = fields.Raw(dump_only=True)
    meetings = fields.Relationship(many=True, dump_only=True)


class UserBpss(BPSchema):
    user = fields.StructuralRef(dm_cls=User)


class UserViewMixin:

    class Meta:
        schema_cls = UserViewSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new(cls, doc_id=None):
        return cls.get_from_user_id(user_id=doc_id)

    @property
    def first_name(self):
        return self.store.user.first_name

    @property
    def last_name(self):
        return self.store.user.last_name

    @last_name.setter
    def last_name(self, new_last_name):
        self.store.user.last_name = new_last_name

    @property
    def organization(self):
        return self.store.user.organization

    @property
    def hearing_aid_requested(self):
        return self.store.user.hearing_aid_requested

    @property
    def meetings(self):
        return list(Meeting.where(users=("array_contains", self.store.user.doc_ref)))

    @classmethod
    def get_from_user_id(cls, user_id, once=False, **kwargs):
        struct = Struct(schema_obj=UserBpss())

        u: User = User.get(doc_id=user_id)

        struct["user"] = (User, u.doc_ref.id)

        return super().get(struct_d=struct, once=once, **kwargs)


class UserView(UserViewMixin, view.FlaskAsView):
    pass
