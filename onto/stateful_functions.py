import logging
from contextvars import ContextVar
from typing import Callable, Union

from onto.helpers import make_variable
import statefun
from statefun import make_json_type, Context, Message, kafka_egress_message
from onto.models.base import Serializable

METHOD_TYPE = make_json_type(typename="example/Method")
EVENT_TYPE = make_json_type(typename="example/Event")

EGRESS_RECORD_TYPE = make_json_type(typename="io.statefun.playground/EgressRecord")

statefun_context_var: Union[ContextVar[statefun.Context], Callable] = make_variable('statefun_context', default=None)
statefun_message_var: Union[ContextVar[statefun.Message], Callable] = make_variable('statefun_message', default=None)


async def do_classmethod(obj_cls: type, classmethod_call):
    function_name = classmethod_call['f']
    parameters = classmethod_call['parameters']
    for k, v in classmethod_call.get('serializable_parameters', dict()).items():
        parameters[k] = Serializable.from_dict(v)
    f = getattr(obj_cls, function_name)
    import inspect
    if inspect.iscoroutinefunction(f):
        return await f(**parameters)
    else:
        return f(**parameters)


async def do_init(obj_cls: type, method_call: dict, storage: Context.storage) -> None:
    res = await do_classmethod(obj_cls, classmethod_call=method_call)
    d: dict = res.to_dict()
    import json
    __d = json.dumps(d)
    storage.__d = __d


async def do_event(obj_cls: type, event: dict, storage: Context.storage, doc_id: str) -> None:
    __d = storage.__d
    if not __d:
        raise TypeError("NULL 未初始化的对象不可调用 do_event")
    import json
    d: dict = json.loads(__d)
    obj = obj_cls.from_dict(d)

    name: str = event['name']  # name = 'rule-hello-world'
    function_name = '_'.join(name.split('-')[1:])  # function_name = 'hello_world'
    f = getattr(obj, function_name)
    import inspect
    if inspect.iscoroutinefunction(f):
        await f(event)
    else:
        f(event)

    d: dict = obj.to_dict()
    import json
    __d = json.dumps(d)
    storage.__d = __d


async def do_method(obj_cls: type, method_call: dict, storage: Context.storage, doc_id: str, should_persist: bool) -> None:
    """
    Invoke a method on the instance

    :param obj_cls: target class
    :param method_call: call configuration
    :param storage: statefun storage object
    :param doc_id: instance doc_id (will not be read. doc_id is spawned from dictionary representation)
    :param should_persist: if True, persist the change and emit a view
    """
    __d = storage.__d
    if not __d:
        raise TypeError("NULL 未初始化的对象不可调用 method")
    import json
    d: dict = json.loads(__d)
    obj = obj_cls.from_dict(d)

    function_name = method_call['f']
    parameters = method_call['parameters']
    for k, v in method_call.get('serializable_parameters', dict()).items():
        parameters[k] = Serializable.from_dict(v)
    f = getattr(obj, function_name)
    import inspect
    if inspect.iscoroutinefunction(f):
        await f(**parameters)
    else:
        f(**parameters)

    if should_persist:
        d: dict = obj.to_dict()
        import json
        __d = json.dumps(d)
        storage.__d = __d


async def do_raw(obj_cls: type, method_call: dict, storage: Context.storage, context: Context, message: Message, should_persist: bool) -> None:
    """
    context and message passthrough as __context__ and __message__
    """
    __d = storage.__d
    if not __d:
        raise TypeError("NULL 未初始化的对象不可调用 method")
    import json
    d: dict = json.loads(__d)
    obj = obj_cls.from_dict(d)

    function_name = method_call['f']
    parameters = method_call['parameters']
    for k, v in method_call.get('serializable_parameters', dict()).items():
        parameters[k] = Serializable.from_dict(v)
    f = getattr(obj, function_name)
    import inspect
    if inspect.iscoroutinefunction(f):
        await f(**parameters, __context__=context, __message__=message)
    else:
        f(**parameters, __context__=context, __message__=message)

    if should_persist:
        d: dict = obj.to_dict()
        import json
        __d = json.dumps(d)
        storage.__d = __d


async def make_event_call(dm_cls: type, context: Context, message: Message, topic: str):
    """
    React to event
    """
    if not message.is_type(EVENT_TYPE):
        raise TypeError('需要是 EVENT_TYPE')
    event = message.as_type(EVENT_TYPE)
    await do_event(dm_cls, event=event, storage=context.storage, doc_id=message.target_id)

    context.send_egress(kafka_egress_message(
        typename='com.example/domain-egress',
        topic=topic,
        key=context.address.id,
        value=context.storage.__d)
    )


async def make_call(dm_cls: type, context: Context, message: Message, topic: str):
    with statefun_context_var(context), statefun_message_var(message):
        if not message.is_type(METHOD_TYPE):
            raise TypeError('需要是 METHOD_TYPE')
        function_call = message.as_type(METHOD_TYPE)
        # If true, persist the change
        should_persist = function_call.get('should_persist', True)
        if function_call['invocation_type'] == 'ClassMethod':
            await do_init(dm_cls, method_call=function_call, storage=context.storage)
        elif function_call['invocation_type'] == 'Method':
            await do_method(dm_cls, method_call=function_call, storage=context.storage, doc_id=message.target_id, should_persist=should_persist)
        elif function_call['invocation_type'] == 'DoNoOpEmit':
            """
            emit a view
            """
            pass
        elif function_call['invocation_type'] == 'RawMethod':
            await do_raw(
                dm_cls,
                method_call=function_call,
                storage=context.storage,
                context=context,
                message=message,
                should_persist=should_persist
            )
        else:
            raise
        if should_persist:
            context.send_egress(kafka_egress_message(
                typename='com.example/domain-egress',
                topic=topic,
                key=context.address.id,
                value=context.storage.__d)
            )


async def send_one(s, topic, target_id: str):
    """ TODO: optimize """
    from aiokafka import AIOKafkaProducer
    producer = AIOKafkaProducer(bootstrap_servers='kafka.kafka.svc.cluster.local:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait(topic, value=s.encode('utf-8'), key=target_id.encode('utf-8'))
    except Exception as e:
        raise
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()


class StatefunProxy:

    def __init__(self, wrapped, target_id: str, invocation_type: str, topic: str, should_persist: bool = True, target_typename=None):
        self.wrapped = wrapped
        self.target_id = target_id
        self.invocation_type = invocation_type
        self.topic = topic
        self.should_persist = should_persist
        self.target_typename = target_typename

    @classmethod
    def method_of(cls, dm_cls: type, target_id: str):
        return cls(
            wrapped=dm_cls,
            target_id=target_id,
            invocation_type='Method',
            topic=f'{dm_cls.__name__.casefold()}-calls-1'
        )

    @classmethod
    def raw_method_of(cls, dm_cls: type, target_id: str):
        return cls(
            wrapped=dm_cls,
            target_id=target_id,
            invocation_type='RawMethod',
            topic=f'{dm_cls.__name__.casefold()}-calls-1'
        )

    @classmethod
    def classmethod_of(cls, dm_cls: type, target_id: str):
        return cls(
            wrapped=dm_cls,
            target_id=target_id,
            invocation_type='ClassMethod',
            topic=f'{dm_cls.__name__.casefold()}-calls-1'
        )

    @classmethod
    def noopemit_of(cls, dm_cls: type, target_id: str):
        return cls(
            wrapped=dm_cls,
            target_id=target_id,
            invocation_type='NoOpEmit',
            topic=f'{dm_cls.__name__.casefold()}-calls-1'
        )

    def _get_make_call_kafka(self, name):

        async def make_call(**kwargs):

            logging.info(f'kafka: {self.invocation_type} id: {self.target_id} f: {name} parameters: {kwargs}')
            res = self._get_invocation_value(f_name=name, _kwargs=kwargs)

            import json
            s = json.dumps(res)
            await send_one(s, self.topic, target_id=self.target_id)

        return make_call

    def _get_invocation_value(self, f_name, _kwargs):
        serializable_parameters = {k: v.to_dict() for k, v in _kwargs.items() if isinstance(v, Serializable)}
        regular_parameters = {k: v for k, v in _kwargs.items() if not isinstance(v, Serializable)}
        res = dict(
            f=f_name,
            parameters=regular_parameters,
            serializable_parameters=serializable_parameters,
            invocation_type=self.invocation_type,
            should_persist=self.should_persist,
        )
        return res

    def _get_make_call_stateful_functions(self, name):

        async def make_call(**kwargs):

            logging.info(f'stateful-functions: {self.invocation_type} id: {self.target_id} f: {name} parameters: {kwargs}')
            res = self._get_invocation_value(f_name=name, _kwargs=kwargs)

            __context__ = statefun_context_var.get()
            from statefun import message_builder

            __context__.send(
                message=message_builder(
                    target_typename=self.target_typename,
                    target_id=self.target_id,
                    value=res,
                    value_type=METHOD_TYPE
                ),
            )

        return make_call

    def __getattr__(self, name):
        from onto.invocation_context import invocation_context_var
        invocation_context = invocation_context_var.get()
        from onto.invocation_context import InvocationContextEnum
        if invocation_context == InvocationContextEnum.KAFKA_TO_FUNCTIONS_INGRESS:
            return self._get_make_call_kafka(name=name)
        elif invocation_context == InvocationContextEnum.STATEFUL_FUNCTIONS_INTERNAL:
            return self._get_make_call_stateful_functions(name=name)
        else:
            raise TypeError(f'unsupported {invocation_context}')



