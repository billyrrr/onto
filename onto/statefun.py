from statefun import make_json_type, Context, Message, kafka_egress_message

METHOD_TYPE = make_json_type(typename="example/Method")

EGRESS_RECORD_TYPE = make_json_type(typename="io.statefun.playground/EgressRecord")


async def do_classmethod(obj_cls: type, classmethod_call):
    function_name = classmethod_call['f']
    parameters = classmethod_call['parameters']
    f = getattr(obj_cls, function_name)
    return f(**parameters)


async def do_init(obj_cls: type, method_call: dict, storage: Context.storage) -> None:
    res = await do_classmethod(obj_cls, classmethod_call=method_call)
    d: dict = res.to_dict()
    import json
    __d = json.dumps(d)
    storage.__d = __d


async def do_method(obj_cls: type, method_call: dict, storage: Context.storage, doc_id: str) -> None:
    __d = storage.__d
    if not __d:
        raise "NULL 未初始化的对象不可调用 method"
    import json
    d: dict = json.loads(__d)
    obj = obj_cls.from_dict(d)

    function_name = method_call['f']
    parameters = method_call['parameters']
    f = getattr(obj, function_name)
    import inspect
    if inspect.iscoroutinefunction(f):
        await f(**parameters)
    else:
        f(**parameters)

    d: dict = obj.to_dict()
    import json
    __d = json.dumps(d)
    storage.__d = __d


async def make_call(dm_cls: type, context: Context, message: Message, topic: str):
    if not message.is_type(METHOD_TYPE):
        raise TypeError('需要是 METHOD_TYPE')
    function_call = message.as_type(METHOD_TYPE)
    if function_call['invocation_type'] == 'ClassMethod':
        await do_init(dm_cls, method_call=function_call, storage=context.storage)
    elif function_call['invocation_type'] == 'Method':
        await do_method(dm_cls, method_call=function_call, storage=context.storage, doc_id=message.target_id)
    elif function_call['invocation_type'] == 'DoNoOpEmit':
        """
        emit a view
        """
        pass
    else:
        raise
    context.send_egress(kafka_egress_message(
        typename='com.example/domain-egress',
        topic=topic,
        key=context.address.id,
        value=context.storage.__d)
    )


async def send_one(s, topic):
    """ TODO: optimize """
    from aiokafka import AIOKafkaProducer
    producer = AIOKafkaProducer(bootstrap_servers='kafka.kafka.svc.cluster.local:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait(topic, value=s.encode('utf-8'), key='a3'.encode('utf-8'))
    except Exception as e:
        raise
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()


class StatefunProxy:

    def __init__(self, wrapped, target_id: str, invocation_type: str, topic: str):
        self.wrapped = wrapped
        self.target_id = target_id
        self.invocation_type = invocation_type
        self.topic = topic

    @classmethod
    def method_of(cls, dm_cls: type, target_id: str):
        return cls(
            wrapped=dm_cls,
            target_id=target_id,
            invocation_type='Method',
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

    def __getattr__(self, name):

        async def make_call(**kwargs):
            print(self.invocation_type)
            print(f'id: {self.target_id} f: {name} parameters: {kwargs}')

            res = dict(f=name, parameters=kwargs, invocation_type=self.invocation_type)
            import json
            s = json.dumps(res)
            await send_one(s, self.topic)

        return make_call


