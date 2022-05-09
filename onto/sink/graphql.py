import asyncio
import weakref
from collections import defaultdict, OrderedDict
from functools import partial
from inspect import Parameter
from typing import Type

from onto.helpers import make_variable
from onto.source.protocol import Protocol
from onto.view_model import ViewModel

from onto.sink.base import Sink


from collections import namedtuple

graph_schema = namedtuple('graph_schema', ['op_type', 'name', 'graphql_object_type', 'args'])
import graphql

graphql_context = make_variable('graphql_context', default=None)


def get_info() -> 'GraphQLResolveInfo':
    return graphql_context.get()


def get_user(info: 'GraphQLResolveInfo'):
    return info.context['request'].user

class GraphQLSink(Sink):

    _protocol_cls = Protocol

    def __set_name__(self, owner, name):
        """ Keeps mediator as a weakref to protect garbage collection
        Note: mediator may be destructed if not maintained or referenced
            by another variable. Mediator needs to be explicitly kept alive.

        TODO: note that parent and sink_name are not initialized

        :param owner:
        :param name:
        :return:
        """
        self.parent = weakref.ref(owner)
        self._name = name

    @property
    def sink_name(self):
        name = self._name
        if self._camelize:
            from onto.utils import camel
            name = camel(name)
        return name

    @property
    def triggers(self):
        return self.protocol

    @property
    def mediator_instance(self):
        return self.parent()()

    def _maybe_deserialize(self, val, annotated_type):
        from onto.models.base import BaseRegisteredModel
        if issubclass(annotated_type, BaseRegisteredModel):
            if isinstance(val, annotated_type):
                return val  # user: User already deserialized
            return annotated_type.from_dict_special(val)
        else:
            return val

    def _f_of_rule(self, func_name):
        fname = self.protocol.fname_of(func_name)
        if fname is None:
            raise ValueError(
                f"fail to locate {func_name}"
                f" for {self.mediator_instance.__class__.__name__}"
            )
        f = getattr(self.mediator_instance, fname)
        return f

    def _invoke_mediator(self, *args, func_name, **kwargs):

        async def trivial():
            """
            A trivial function to prevent calling await on None
            """
            return None

        try:
            f = self._f_of_rule(func_name=func_name)
        except ValueError as e:
            import logging
            logging.exception('mediator not located')
            return trivial()

        annotation_d = {
            k: v
            for k, v in self._parameters_for(f)
        }

        new_kwargs = {
            k:self._maybe_deserialize(val=v, annotated_type=annotation_d[k]) if k in annotation_d else v
            for k, v in kwargs.items()
        }

        try:
            return f(*args, **new_kwargs)
        except Exception as e:
            import logging
            logging.exception('_invoke mediator failed for graphql subscription')

            return trivial() # TODO: return something else

    def __init__(self, view_model_cls: Type[ViewModel], camelize=True, many=False):
        """

        :param view_model_cls:
        :param camelize:
        """
        self.protocol = self._protocol_cls()
        self.view_model_cls = view_model_cls
        import asyncio
        loop = asyncio.get_event_loop()
        from functools import partial
        cons = partial(asyncio.Queue
                       # , loop=loop
                       )

        from onto.sink.utils import Broker
        self.broker = Broker()
        self.loop = loop
        self._camelize = camelize
        self.many = many
        super().__init__()

    @property
    def qs(self):
        raise TypeError(
            """
            qs is deprecated.
            instead of ``` self.sink.qs[topic_name] = item ```, use:
            ```await self.sink.publish(topic_name, item) ```
            """
        )

    @staticmethod
    def _param_to_graphql_arg(annotated_type):
        from onto.models.utils import _graphql_type_from_py
        from graphql import GraphQLArgument, GraphQLInputObjectType
        # TODO: add notes about `typing.*` not supported
        gql_field_cls = _graphql_type_from_py(annotated_type, input=True)
        arg = GraphQLArgument(gql_field_cls)  # TODO: set default_value
        return arg

    @staticmethod
    def _parameters_for(f):

        def _annotation_type_of(param):
            annotation = param.annotation
            import inspect
            if annotation is inspect._empty:
                import warnings
                warnings.warn(f'parameter {param} is not annotated'
                                 ' for conversion to graphql argument')
                return None
            return annotation

        from inspect import signature
        sig = signature(f)
        param_d = OrderedDict(sig.parameters.items())
        # param_d.popitem(last=False)  # Pop self argument
        # NOTE: param_d.popitem(last=False) may not always pop self argument
        for name, param in param_d.items():
            typ = _annotation_type_of(param)
            if typ is not None:
                yield name, typ
        yield from ()

    def _args_of_f(self, f):
        for name, annotated_type in self._parameters_for(f):
            yield name, self._param_to_graphql_arg(annotated_type=annotated_type)
        yield from ()

    def _args_of(self, rule):
        f = self._f_of_rule(func_name=rule)
        return self._args_of_f(f=f)

    op_type = None

    def _as_graphql_schema(self):
        from onto.models.utils import \
            _graphql_object_type_from_attributed_class
        attributed = self.view_model_cls

        ot = attributed.get_graphql_object_type(is_input=False)

        if self.many:
            ot = graphql.GraphQLList(type_=ot)

        name, args = self._register_op()

        return graph_schema(
            op_type=self.op_type,
            name=name,
            graphql_object_type=ot,
            args=args
        )

    def start(self):
        subscription_schema = self._as_graphql_schema()
        return subscription_schema

    _get_user = staticmethod(get_user)



class GraphQLSubscriptionSink(GraphQLSink):

    op_type = 'Subscription'

    @staticmethod
    def _get_user(info):
        return info.context.user

    async def publish(self, *args, **kwargs):
        return await self.broker.publish(*args, **kwargs)

    def start(self, loop):
        _ = asyncio.run_coroutine_threadsafe(
            self.broker.source_while_loop(), loop=loop
        )
        return super().start()

    def _register_op(self):
        from gql import subscribe
        async def f(parent, info, **kwargs):
            kwargs = {
                'user': self._get_user(info),
                'info': info,
                **kwargs,
            }
            # Register topic
            topic_name = await self._invoke_mediator(func_name='add_topic', **kwargs)

            # Perform before_subscription
            await self._invoke_mediator(func_name='before_subscription', **kwargs)

            from onto.utils import random_id
            sub_id = random_id()

            self.broker.bind(pub_id=topic_name, sub_id=sub_id)
            async for event in self.broker.sink_while_loop(sub_id=sub_id):
                yield {
                    self.sink_name:
                        self._invoke_mediator(func_name='on_event',
                                              event=event, **kwargs)
                }

        # name = self.parent().__name__
        # f.__name__ = name
        name = self.sink_name
        f.__name__ = name
        subscribe(f)
        args = dict(self._args_of('add_topic'))

        return name, args


class GraphQLQuerySink(GraphQLSink):

    op_type = 'Query'

    def _register_op(self):
        from gql import query
        extra_args = set()

        async def f(parent, info, **kwargs):
            kwargs = {
                'info': info,
                **kwargs,
            }

            try:
                user = self._get_user(info)
                kwargs['user'] = user
            except:
                import logging
                logging.error('未能解析user，可能是没有装载 AuthMiddleware；程序将继续执行以兼容不需要用户的测试代码')

            res = await self._invoke_mediator(func_name='query', **kwargs)
            return res

        name = self.sink_name
        f.__name__ = name
        query(f)
        args = dict(self._args_of('query'))
        return name, args


class GraphQLMutationSink(GraphQLSink):

    op_type = 'Mutation'

    def _register_op(self):
        from gql import mutate

        extra_args = set()
        async def f(parent, info, **kwargs):
            kwargs = {
                'user': self._get_user(info),
                'info': info,
                **kwargs
            }
            with graphql_context(info):
                res = await self._invoke_mediator(func_name='mutate', **kwargs)
            return res

        name = self.sink_name
        f.__name__ = name
        mutate(f, snake_argument=False)
        args = dict(self._args_of('mutate'))
        return name, args


def op_schema(op_type, schema_all):
    from onto.helpers.graphql import default_field_resolver

    ot = graphql.GraphQLObjectType(
        name=op_type,
        fields={
            schema.name:
                graphql.GraphQLField(
                    schema.graphql_object_type,
                    resolve=default_field_resolver,
                    args=schema.args)
            for schema in schema_all
            if schema.op_type == op_type
        }
    )
    return ot


query = GraphQLQuerySink
mutation = GraphQLMutationSink
subscription = GraphQLSubscriptionSink
