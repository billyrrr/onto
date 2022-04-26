import logging

from onto.source.base import Source


async def _kafka_subscribe(topic_name, callback, bootstrap_servers='kafka.default.svc.cluster.local:9092'):
    from aiokafka import AIOKafkaConsumer

    def key_deserializer(v: bytes):
        return v.decode("utf-8")

    def value_deserializer(v: bytes):
        import json
        s = v.decode('utf-8')
        return json.loads(s)

    consumer = AIOKafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        key_deserializer=key_deserializer,
        value_deserializer=value_deserializer
        # group_id="my-group"
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    # TODO: make first yield when listener has started
    try:
        # Consume messages
        async for msg in consumer:
            await callback(message=msg)
            # print("consumed: ", msg.topic, msg.partition, msg.offset,
            #       msg.key, msg.value, msg.timestamp)
    except Exception as e:
        import warnings
        logging.exception('invoke kafka failed')
        raise ValueError('Interrupted') from e
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


class KafkaSource(Source):

    def __init__(self, topic_name, bootstrap_servers='kafka.default.svc.cluster.local:9092', **kwargs):
        """ Initializes a ViewMediator to declare protocols that
                are called when the results of a query change. Note that
                mediator.start must be called later.

        :param query: a listener will be attached to this query
        """
        super().__init__(**kwargs)
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers

    def start(self, loop):
        import asyncio
        # tell asyncio to enqueue the result
        _ = asyncio.run_coroutine_threadsafe(
            self._register(), loop=loop
        )

    async def _register(self):
        from functools import partial
        f = partial(self._invoke_mediator_async, func_name='on_topic')
        await _kafka_subscribe(topic_name=self.topic_name, callback=f, bootstrap_servers=self.bootstrap_servers)


class KafkaDomainModelSource(KafkaSource):

    def __init__(self, *, dm_cls, **kwargs, ):
        self.dm_cls = dm_cls
        super().__init__(**kwargs)


    async def _invoke_mediator_async(self, *, func_name, message: 'ConsumerRecord'):
        k = message.key
        v = message.value
        obj = self.dm_cls.from_dict(v)
        # obj.doc_id = k
        try:
            await super()._invoke_mediator_async(func_name=func_name, obj=obj)
        except Exception as _:
            import logging
            logging.exception(f'async _invoke_mediator failed for {func_name} {str(k)}')


