from examples.meeting_room.views.graphql_view import UserGraphQLMediator
from onto.sink.graphql import op_schema

schema_all = list()

schema_all += UserGraphQLMediator.start()

from graphql import GraphQLSchema

schema = GraphQLSchema(
    query=op_schema(op_type='Query', schema_all=schema_all),
    subscription=op_schema(op_type='Subscription', schema_all=schema_all)
)

from stargql import GraphQL

app = GraphQL(
    schema=schema,
)

# PYTEST FIXTURES: RETAIN
from tests.fixtures import CTX
from examples.meeting_room.tests.fixtures import users, meeting, location, tickets


def test_run(users, meeting, location, tickets):

    import asyncio
    loop = asyncio.get_event_loop()

    from uvicorn import Config
    config = Config(app=app, loop=loop, port=8080, debug=True)
    from uvicorn import Server
    server = Server(config)
    loop.run_until_complete(server.serve())

    # uvicorn.run(app, port=8080, debug=True)
