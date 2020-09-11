import weakref
from collections import defaultdict
from typing import Type

from flask_boiler.source.protocol import Protocol
from flask_boiler.view_model import ViewModel

from flask_boiler.sink.base import Sink


from collections import namedtuple

graph_schema = namedtuple('graph_schema', ['op_type', 'name', 'graphql_object_type'])


class GraphQLSink(Sink):

    _protocol_cls = Protocol

    def __set_name__(self, owner, name):
        """ Keeps mediator as a weakref to protect garbage collection
        Note: mediator may be destructed if not maintained or referenced
            by another variable. Mediator needs to be explicitly kept alive.

        :param owner:
        :param name:
        :return:
        """
        self.parent = weakref.ref(owner)

    @property
    def triggers(self):
        return self.protocol

    @property
    def mediator_instance(self):
        return self.parent()()

    def _invoke_mediator(self, *args, func_name, **kwargs):
        fname = self.protocol.fname_of(func_name)
        if fname is None:
            raise ValueError(f"fail to locate {func_name} for {self.mediator_instance.__class__.__name__}")
        f = getattr(self.mediator_instance, fname)
        return f(*args, **kwargs)

    def __init__(self, view_model_cls: Type[ViewModel]):
        self.protocol = self._protocol_cls()
        self.view_model_cls = view_model_cls
        import asyncio
        loop = asyncio.get_event_loop()
        from functools import partial
        cons = partial(asyncio.Queue, loop=loop)
        self.qs = defaultdict(cons)
        self.loop = loop
        super().__init__()

    def start(self):
        from flask_boiler.models.utils import \
            _graphql_object_type_from_attributed_class
        attributed = self.view_model_cls

        graphql_schema = _graphql_object_type_from_attributed_class(attributed)

        from gql import query, subscribe

        async def f(parent, info, **kwargs):
            # Register topic
            topic_name = self._invoke_mediator(func_name='add_topic', **kwargs)
            # Listen to topic
            q = self.qs[topic_name]

            while True:
                event = await q.get()
                yield self._invoke_mediator(func_name='on_event', event=event)

        name = self.parent().__class__.__name__
        f.__name__ = name
        subscribe(f)

        return graph_schema(
            op_type='Subscription',
            name=name,
            graphql_object_type=graphql_schema
        )

        # subscription_schema = GraphQLObjectType(
        #     name='Subscription',
        #     fields={
        #         'h': graphql_schema
        #     }
        # )

