import asyncio
from datetime import datetime
# from graphene import ObjectType, String, Schema, Field
from aiokafka import AIOKafkaConsumer
from stargql.subscription import Subscription

from onto.source.base import Source

"""
[Start] Sample code from aiokafka 
ref: https://github.com/aio-libs/aiokafka 
"""
loop = asyncio.get_event_loop()
async def _kafka_subscribe(topic_name):
    consumer = AIOKafkaConsumer(
        topic_name,
        bootstrap_servers='localhost:9092',
        # group_id="my-group"
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    # TODO: make first yield when listener has started
    try:
        # Consume messages
        async for msg in consumer:
            yield msg
            # print("consumed: ", msg.topic, msg.partition, msg.offset,
            #       msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()
loop.run_until_complete(_kafka_subscribe(topic_name='my-topic'))


"""
[End] Sample code from aiokafka 
Ref: https://github.com/aio-libs/aiokafka
"""

# # Every schema requires a query.
# class Query(ObjectType):
#     hello = String()
#
#     def resolve_hello(root, info):
#         return "Hello, world!"
#
#
# class Subscription(ObjectType):
#     time_of_day = String()
#
#     async def subscribe_time_of_day(root, info):
#         while True:
#             yield datetime.now().isoformat()
#             await asyncio.sleep(1)
# schema = Schema(query=Query, subscription=Subscription)

async def main(schema):
    subscription = 'subscription { timeOfDay }'
    result = await schema.subscribe(subscription)
    async for item in result:
        print(item.data['timeOfDay'])

# asyncio.run(main(schema))

#
# def _as_graphql_root_schema(attributed):
#     from graphql import GraphQLSchema
#
#     from onto.models.utils import _graphql_object_type_from_attributed_class
#     graphql_ot = _graphql_object_type_from_attributed_class(attributed)
#
#     async def sub(parent, info, **kwargs):
#         pass
#
#     schema = GraphQLSchema(
#         query=graphql_ot,
#         subscription=Subscription
#     )
#
#     from graphql.subscription import create_source_event_stream
#     create_source_event_stream(schema=schema, document=schema.ast_node, )
#     _ = subscribe(schema=schema, subscribe_field_resolver=sub)
#
#     return schema


class GraphQLSource(Source):

    def __init__(self, attributed_cls):
        super().__init__()
        self.attributed_cls = attributed_cls

    def start(self):
        schema = _as_graphql_root_schema(self.attributed_cls)
        from stargql import GraphQL

        async def on_startup():
            from asyncio.queues import Queue
            global q
            q = Queue()

        async def shutdown():
            pass

        app = GraphQL(
            schema=schema,
            on_startup=[on_startup],
            on_shutdown=[shutdown]
        )
        return app


#
# class KafkaSource(Source):
#
#     # def __init__(self, query):
#     #     """ Initializes a ViewMediator to declare protocols that
#     #             are called when the results of a query change. Note that
#     #             mediator.start must be called later.
#     #
#     #     :param query: a listener will be attached to this query
#     #     """
#     #     super().__init__()
#     #     self.query = query
#
#     def start(self):
#         self._register()
#
#     def _register(self):
#         res = _kafka_subscribe(self.topic_name, self._call)
#         asyncio.run(res)
#         async for item in res:
#
#     @classmethod
#     def delta(cls, container):
#         start = container._read_times[-2]
#         end = container._read_times[-1]
#         for key in container.d.keys():
#             for snapshot in container.get_with_range(key, start, end):
#                 from onto.database import Snapshot
#                 prev: Snapshot = snapshot.prev
#                 cur: Snapshot = snapshot
#                 if not prev.exists:
#                     yield ("on_create", key, cur)
#                 elif prev.exists and cur.exists:
#                     yield ("on_update", key, cur)
#                 elif prev.exists and not cur.exists:
#                     yield ("on_delete", key, cur)
#                 else:
#                     raise ValueError
#
#     def _call(self, msg):
#         self._invoke_mediator(
#             func_name=func_name, ref=ref, snapshot=snapshot)
