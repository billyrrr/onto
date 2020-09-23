from onto.attrs import attribute

from onto.models.base import Serializable


class H(Serializable):

    i = attribute.Attribute(type_cls=int, doc="I am 'i'.")

    j = attribute.PropertyAttribute(
        type_cls=str,
        doc="""I am 'j'. See next line. 
    This is my second line. 
    """
    )


from collections import namedtuple

graph_schema = namedtuple('graph_schema', ['op_type', 'name', 'graphql_object_type'])


def test__schema_cls_from_attributed_class():
    # import asyncio
    # loop = asyncio.get_event_loop()

    from onto.models.utils import _graphql_object_type_from_attributed_class
    attributed = H

    graphql_schema = _graphql_object_type_from_attributed_class(attributed)

    async def sub(parent, info, **kwargs):
        pass
    #
    from graphql import GraphQLObjectType
    query_schema = GraphQLObjectType(
        name='Query',
        fields={
            'h': graphql_schema
        }
    )

    from gql import query, subscribe

    @query
    async def h(parent, info, **kwargs):
        return {
            'i': 1,
            'j': 'one'
        }

    graph_schema(op_type='Query', name='h', graphql_object_type=graphql_schema)

    @subscribe
    async def h(parent, info, **kwargs):
        # Register topic
        # Listen to topic 
        for i in range(5):
            import asyncio
            await asyncio.sleep(i)
            yield {
                'h': {
                    'i': i,
                    'j': f"number is {i}"
                }

            }


    subscription_schema = GraphQLObjectType(
        name='Subscription',
        fields={
            'h': graphql_schema
        }
    )

    from graphql import GraphQLSchema
    schema = GraphQLSchema(
        query=query_schema,
        subscription=subscription_schema
    )

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

    # import uvicorn
    # uvicorn.run(app, port=8080, debug=True)
    # return app
