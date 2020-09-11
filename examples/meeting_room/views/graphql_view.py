import uvicorn as uvicorn
from examples.meeting_room.domain_models import User

from examples.meeting_room.view_models import UserView
from flask_boiler.view import Mediator


class UserGraphQLMediator(Mediator):

    from flask_boiler.source import domain_model
    from flask_boiler.sink.graphql import GraphQLSink

    src = domain_model(domain_model_cls=User)
    sink = GraphQLSink(view_model_cls=UserView)

    @sink.triggers.add_topic
    def add_topic(self, user_id=None):
        return user_id

    @sink.triggers.on_event
    def on_event(self, event: dict):
        return event

    @src.triggers.on_create
    @src.triggers.on_update
    def user_updated(self, obj: User):
        v = UserView.get(user_id=obj.doc_id)
        d = v.to_dict()

        import asyncio
        # tell asyncio to enqueue the result
        fut = asyncio.run_coroutine_threadsafe(
            self.sink.qs[obj.doc_id].put(d), loop=self.sink.loop
        )
        # wait for the result to be enqueued
        fut.result()

    @classmethod
    def start(cls):
        cls.src.start()
        return cls.sink.start()
