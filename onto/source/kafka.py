from onto.source.base import Source


async def _kafka_subscribe(topic_name):
    from aiokafka import AIOKafkaConsumer
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


class KafkaSource(Source):

    def __init__(self, topic_name):
        """ Initializes a ViewMediator to declare protocols that
                are called when the results of a query change. Note that
                mediator.start must be called later.

        :param query: a listener will be attached to this query
        """
        super().__init__()
        self.topic_name = topic_name

    def start(self, loop):
        import asyncio
        # tell asyncio to enqueue the result
        _ = asyncio.run_coroutine_threadsafe(
            self._register(), loop=loop
        )

    async def _register(self):
        async for message in _kafka_subscribe(topic_name=self.topic_name):
            self._invoke_mediator(func_name='on_topic', message=message)
