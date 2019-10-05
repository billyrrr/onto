from examples.meeting_room.domain_models.user import User
from examples.meeting_room.domain_models.meeting import Meeting
from flask_boiler import fields, schema, view_model, view


class UserViewSchema(schema.Schema):

    first_name = fields.Raw(dump_only=True)
    last_name = fields.Raw(dump_only=True)
    organization = fields.Raw(dump_only=True)

    hearing_aid_requested = fields.Raw(dump_only=True)
    meetings = fields.Relationship(many=True, dump_only=True)


class UserView(view.FlaskAsViewMixin, view_model.ViewModel):

    _schema_cls = UserViewSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new(cls, doc_id=None):
        return cls.get_from_user_id(user_id=doc_id)

    def set_user(self, user):
        self.user = user

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def organization(self):
        return self.user.organization

    @property
    def hearing_aid_requested(self):
        return self.user.hearing_aid_requested

    @property
    def meetings(self):
        return list(Meeting.where(users=("array_contains", self.user.doc_ref)))

    @classmethod
    def get_from_user_id(cls, user_id, once=False):
        struct = dict()

        u: User = User.get(doc_id=user_id)

        def user_update_func(vm: UserView, dm):
            vm.set_user(dm)
        struct[u.doc_id] = ("User", u.doc_ref.id, user_update_func)

        return super().get(struct_d=struct, once=once)
