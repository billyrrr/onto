import weakref
from collections import defaultdict, OrderedDict
from inspect import Parameter
from typing import Type

from flask_boiler.source.protocol import Protocol
from flask_boiler.view_model import ViewModel

from flask_boiler.sink.base import Sink


from collections import namedtuple

graph_schema = namedtuple('graph_schema', ['op_type', 'name', 'graphql_object_type', 'args'])
import graphql


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
            from flask_boiler.utils import camel
            name = camel(name)
        return name

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

    def __init__(self, view_model_cls: Type[ViewModel], camelize=True):
        """

        :param view_model_cls:
        :param camelize:
        """
        self.protocol = self._protocol_cls()
        self.view_model_cls = view_model_cls
        import asyncio
        loop = asyncio.get_event_loop()
        from functools import partial
        cons = partial(asyncio.Queue, loop=loop)
        self.qs = defaultdict(cons)
        self.loop = loop
        self._camelize = camelize
        super().__init__()

    def _param_to_graphql_arg(self, param: Parameter):
        from flask_boiler.models.utils import _graphql_type_from_py
        from graphql import GraphQLArgument
        annotation = param.annotation
        import inspect
        if annotation is inspect._empty:
            raise ValueError('parameter {param} is not annotated'
                             'for conversion to graphql argument')
        # TODO: add notes about `typing.*` not supported
        gql_field_cls = _graphql_type_from_py(annotation)
        arg = GraphQLArgument(gql_field_cls)  # TODO: set default_value
        return arg

    def _args_of(self, rule):
        from inspect import signature
        fname = self.triggers.fname_of(rule)
        f = getattr(self.parent(), fname)
        sig = signature(f)
        param_d = OrderedDict(sig.parameters.items())
        param_d.popitem(last=False)  # Pop self argument
        # NOTE: param_d.popitem(last=False) may not always pop self argument
        for name, param in param_d.items():
            yield name, self._param_to_graphql_arg(param)

    def _as_graphql_schema(self):
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
                yield {
                    self.sink_name:
                    self._invoke_mediator(func_name='on_event', event=event)
                }

        # name = self.parent().__name__
        # f.__name__ = name
        name = self.sink_name
        f.__name__ = name
        subscribe(f)

        args = dict(self._args_of('add_topic'))

        return graph_schema(
            op_type='Subscription',
            name=name,
            graphql_object_type=graphql_schema,
            args=args
        )

    def start(self):
        subscription_schema = self._as_graphql_schema()
        return subscription_schema


def op_schema(op_type, schema_all):
    ot = graphql.GraphQLObjectType(
        name=op_type,
        fields={
            schema.name:
                graphql.GraphQLField(
                    schema.graphql_object_type,
                    args=schema.args)
            for schema in schema_all
            if schema.op_type == op_type
        }
    )
    return ot
