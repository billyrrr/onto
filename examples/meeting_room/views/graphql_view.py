import uvicorn as uvicorn
from examples.meeting_room.domain_models import User

from examples.meeting_room.view_models import UserView
from onto import view_model, attrs
from onto.view import Mediator


class UserGraphQLMediator(Mediator):

    from onto.source import domain_model
    from onto.sink.graphql import subscription

    # src = domain_model(domain_model_cls=User)
    from onto.source.kafka import KafkaSource
    # src = KafkaSource(topic_name='users')
    from onto.source.mock import MockDomainModelSource
    src = MockDomainModelSource(User)
    subscribe_user_view = subscription(view_model_cls=UserView)

    @subscribe_user_view.triggers.add_topic
    def add_topic(self, user_id: str):
        return user_id

    @subscribe_user_view.triggers.on_event
    def on_event(self, event: dict):
        return event

    @src.triggers.on_create
    async def user_added(self, obj):
        q = self.subscribe_user_view.qs[obj.doc_id]
        d = obj.to_dict()
        await q.put(d)
        # import asyncio
        # # tell asyncio to enqueue the result
        # fut = asyncio.run_coroutine_threadsafe(
        #     , loop=self.subscribe_user_view.loop
        # )
        # # wait for the result to be enqueued
        # _ = fut.result()

    # @src.triggers.on_topic
    # def user_updated(self, message):
    #     # v = UserView.get(user_id=obj.doc_id)
    #     # d = v.to_dict()
    #     print(message)
    #     # raise ValueError(str(message))
    #     # User.from_dict(d=d)
    #     # q = self.subscribe_user_view.qs[obj.doc_id]
    #     #
    #     # import asyncio
    #     # # tell asyncio to enqueue the result
    #     # fut = asyncio.run_coroutine_threadsafe(
    #     #     q.put(d), loop=self.subscribe_user_view.loop
    #     # )
    #     # # wait for the result to be enqueued
    #     # _ = fut.result()

    @classmethod
    def start(cls):
        # cls.src.start()

        import asyncio
        loop = asyncio.get_event_loop()
        cls.src.start(loop=loop)

        s = cls.subscribe_user_view.start()
        from onto.sink.graphql import graph_schema
        import graphql
        liveness = graph_schema(
            op_type='Query',
            name='liveness',
            graphql_object_type=graphql.GraphQLObjectType(
                name='Liveness',
                fields={
                    'alive': graphql.GraphQLField(
                        graphql.GraphQLBoolean,
                        resolve=lambda *args, **kwargs: True),
                }
            ),
            args=dict()
        )

        return [s, liveness]


class LoginForm(view_model.ViewModel):
    phone_number = attrs.bproperty(type_cls=str)
    verification_code = attrs.bproperty(type_cls=str)


from onto.attrs import attrs
class LoginRes(view_model.ViewModel):
    token = attrs.of_type(str)


class UserAddMediator(Mediator):

    from onto.sink.graphql import mutation

    login_user_view = mutation(view_model_cls=LoginRes)

    @login_user_view.triggers.mutate
    def login(self, user_id: str, first_name: str, last_name: str, org: str):
        user = User.new(
            doc_id=user_id, first_name=first_name,
            last_name=last_name, organization=org,
            hearing_aid_requested=True
        )
        user.save()

        return LoginRes.new(
            token='supposed to be token for user added'
        )

    @classmethod
    def start(cls):
        s = cls.login_user_view.start()
        return [s]


class UserLoginMediator(Mediator):

    from onto.sink.graphql import mutation

    login_user_view = mutation(view_model_cls=LoginRes)

    @login_user_view.triggers.mutate
    def login(self, form: LoginForm):
        print(form)

    @classmethod
    def start(cls):
        s = cls.login_user_view.start()
        return [s]


