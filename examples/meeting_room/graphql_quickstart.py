from examples.meeting_room.views.graphql_view import UserGraphQLMediator, UserLoginMediator, UserAddMediator
from onto.sink.graphql import op_schema

# PYTEST FIXTURES: RETAIN
from tests.fixtures import CTX
from examples.meeting_room.tests.fixtures import users, meeting, location, tickets

from tests.test_kafka import kafka_server, zookeeper_proc, kafka_consumer


def test_run(users):
    schema_all = list()

    schema_all += UserGraphQLMediator.start()
    schema_all += UserAddMediator.start()
    # schema_all += UserLoginMediator.start()
    #
    from graphql import GraphQLSchema

    schema = GraphQLSchema(
        query=op_schema(op_type='Query', schema_all=schema_all),
        subscription=op_schema(op_type='Subscription', schema_all=schema_all),
        mutation=op_schema(op_type='Mutation', schema_all=schema_all)
    )

    from stargql import GraphQL

    app = GraphQL(
        schema=schema,
    )

    import asyncio
    loop = asyncio.get_event_loop()

    from uvicorn import Config
    config = Config(app=app, loop=loop, port=8081, debug=True)
    from uvicorn import Server
    server = Server(config)

    # from kafka import KafkaProducer
    # kafka_server = KafkaProducer(bootstrap_servers='10.10.8.140:9092')
    # kafka_server.send('users', value='hello world!'.encode('utf-8'))

    loop.run_until_complete(server.serve())

    # uvicorn.run(app, port=8080, debug=True)
