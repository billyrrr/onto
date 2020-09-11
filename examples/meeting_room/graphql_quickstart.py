from examples.meeting_room.views.graphql_view import UserGraphQLMediator


subscription_schema = UserGraphQLMediator.start()

from graphql import GraphQLSchema, GraphQLObjectType, GraphQLField, \
    GraphQLString

import graphql

args = {
    'user_id': graphql.GraphQLArgument(graphql.GraphQLString)
}
ot = GraphQLObjectType(
    name=subscription_schema.op_type,
    fields={
        subscription_schema.name: graphql.GraphQLField(subscription_schema.graphql_object_type, args=args)

    }
)

schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='Query',
        fields={
            'h': GraphQLField(GraphQLString)
        }
    ),
    subscription=ot
)

from stargql import GraphQL


async def on_startup():
    pass


async def shutdown():
    pass


app = GraphQL(
    schema=schema,
    on_startup=[on_startup],
    on_shutdown=[shutdown]
)

from tests.fixtures import CTX
from examples.meeting_room.tests.fixtures import users, meeting, location, tickets


def test_run(users, meeting, location, tickets):

    import uvicorn
    uvicorn.run(app, port=8080, debug=True)
