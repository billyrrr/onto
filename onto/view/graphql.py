import functools
from abc import abstractmethod

import typing
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from . import Mediator
from .. import view_model
import graphql
from gql import gql, subscribe, mutate



# @subscribe
# async def post_added(parent, info, **kwargs):
#     """
#
#     # Write your query or mutation here
#     subscription onPostAdded {
#       postAdded(author: "hello") {
#         author
#       }
#     }
#
#     :param parent:
#     :param info:
#     :param kwargs:
#     :return:
#     """
#     while True:
#         d = await q.get()
#         yield {
#             'postAdded': d
#         }
#
#
# @mutate
# async def add_post(parent, info, **kwargs):
#     """
#
#     # Write your query or mutation here
#     mutation M($author: String, $comment: String) {
#       addPost(author: $author, comment: $comment) {
#         author
#         comment
#       }
#     }
#
#     # Variables
#     {
#       "author": "hello",
#       "comment": "world"
#     }
#
#     :param parent:
#     :param info:
#     :param kwargs:
#     :return:
#     """
#     await q.put(kwargs)
#     return kwargs


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


async def _kafka_publish(topic_name, value):
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        # group_id="my-group"
    )
    await producer.send(topic=topic_name, value=value)


# class TaskManagementMixin:
#
#     # NOTE: queues here are Last-In-First-Out
#     queues: Dict[str, asyncio.LifoQueue] = dict()
#
#     def _enqueue(self, topic_name, item, ):
#         q = self.queues[topic_name]
#         q.put(item=item)
#
#     def _clear_queue(self, q: asyncio.LifoQueue):
#         while not q.empty():
#             q.get_nowait()
#
#     def _dequeue(self, topic_name):
#         """
#         (Fast-forwarding)
#
#         Clears all but the last element in the queue;
#         Returns the last element.
#         :return:
#         """
#         q = self.queues[topic_name]
#         res = q.get()
#         self._clear_queue(q)
#         return res
#


def graphql_ot_from_view_model(t: typing.Type[view_model.ViewModel]) -> graphql.GraphQLObjectType:
    import marshmallow
    schema: marshmallow.Schema = t.get_schema_obj()
    ot = graphql.GraphQLObjectType(
        name=t.__name__,  # TODO: refactor
        fields={
            k: graphql.GraphQLField(graphql.GraphQLString, )
            for k, v in schema.fields.items()
        }
    )
    return ot


# from kafka import KafkaProducer
#
# # assert isinstance(kafka_server, KafkaProducer)
# kafka_server = KafkaProducer(bootstrap_servers='localhost:9092', api_version=(0, 10, 1))


class GraphQLMediator(Mediator):
    """
    Assumptions:
        - only latest state matters for `state = f([state_snapshot])`

    """

    view_model_cls: typing.Type[view_model.ViewModel] = None
    """ Abstract property """

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _get_graphql_field(cls):
        async def add_post(parent, info, **kwargs):
            await _kafka_publish('my-topic', 'world')

        async def post_added(root, info):
            topic_name = 'my-topic'  # TODO: implement
            gen = _kafka_subscribe(topic_name=topic_name)
            async for msg in gen:
                yield cls._invoke(msg=msg)

        # graphql.GraphQLFieldResolver

        return graphql.GraphQLField(
            graphql_ot_from_view_model(cls.view_model_cls),
            resolve=add_post, subscribe=post_added
        )

    @classmethod
    def _get_graphql_schema(cls) -> graphql.GraphQLSchema:

        # schema = graphql.GraphQLObjectType(
        #     subscription=subscribe_content
        # )

        # @mutate
        #
        #
        # @subscribe

        schema = graphql.GraphQLSchema(
            query=graphql.GraphQLObjectType('posts', {
                    "content": cls._get_graphql_field()
                }),
            mutation=graphql.GraphQLObjectType('addPost', {
                    "content": cls._get_graphql_field()
                }),
            subscription=graphql.GraphQLObjectType(
                "postAdded",
                {
                    "content": cls._get_graphql_field()
                },
            ),
        )
        return schema

    @classmethod
    def start(cls):
        """ Registers a GraphQL service
        TODO: catch when user starts the same mediator twice

        :return:
        """

        async def on_startup():
            from asyncio.queues import Queue
            global q
            q = Queue()

        async def shutdown():
            pass

        from stargql import GraphQL
        app = GraphQL(
            schema=cls._get_graphql_schema(),
            on_startup=[on_startup],
            on_shutdown=[shutdown]
        )
        return app

        # app.add_url_rule(rule, view_func=GraphQLView.as_view(
        #     name,
        #     schema=schema,
        #     graphiql=True,
        # ))

    @classmethod
    def _invoke(cls, msg):
        cls.invoke(msg.topic, msg.key, msg.value)

    @classmethod
    @abstractmethod
    def invoke(cls, *args, **kwargs):
        pass


class LivenessMediator(Mediator):

    @classmethod
    def start(cls):
        # TODO: recover cls.src.start()
        # cls.src.start()
        # s = cls.subscribe_user_view.start()
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

        return [liveness]
