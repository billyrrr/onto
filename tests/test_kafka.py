from functools import partial
from pathlib import Path
from subprocess import Popen

from pytest_kafka import (
    make_zookeeper_process, make_kafka_server, make_kafka_consumer,
    terminate,
)

ROOT = Path.cwd()
KAFKA_SCRIPTS = ROOT / 'pytest-kafka-0.4.0' / 'kafka/bin/'
KAFKA_BIN = str(KAFKA_SCRIPTS / 'kafka-server-start.sh')
ZOOKEEPER_BIN = str(KAFKA_SCRIPTS / 'zookeeper-server-start.sh')
# You can pass a custom teardown function (or parametrise ours). Just don't call it `teardown`
# or Pytest will interpret it as a module-scoped teardown function.
teardown_fn = partial(terminate, signal_fn=Popen.kill)
zookeeper_proc = make_zookeeper_process(ZOOKEEPER_BIN, teardown_fn=teardown_fn)
kafka_server = make_kafka_server(KAFKA_BIN, 'zookeeper_proc', kafka_port=9092,
                                 teardown_fn=teardown_fn)
kafka_consumer = make_kafka_consumer(
    'kafka_server', seek_to_beginning=True, kafka_topics=['topic'])


def test_fixture(kafka_server):
    from kafka import KafkaProducer

    # assert isinstance(kafka_server, KafkaProducer)
    kafka_server = KafkaProducer(bootstrap_servers='localhost:9092',
                                 api_version=(0, 10, 1))
    kafka_server.send('my-topic', value='hello world!'.encode('utf-8'))


def test_start(kafka_server):
    from onto.source.kafka import KafkaSource
    src = KafkaSource(topic_name='my-topic')
    import asyncio
    loop = asyncio.get_event_loop()
    src.start(loop=loop)

    # Send something on Kafka
    from kafka import KafkaProducer
    kafka_server = KafkaProducer(bootstrap_servers='localhost:9092',
                                 api_version=(0, 10, 1))
    kafka_server.send('my-topic', value='hello world!'.encode('utf-8'))

    # # Run trivial uvicorn
    # import asyncio
    # loop = asyncio.get_event_loop()
    # from starlette.applications import Starlette
    # app = Starlette()
    # from uvicorn import Config
    # config = Config(app=app, loop=loop, port=8080, debug=True)
    # from uvicorn import Server
    # server = Server(config)
    # loop.run_until_complete(server.serve())


def test__register():
    from unittest.mock import patch
    import onto.source.kafka

    async def _mock_subscribe():
        """
        https://docs.python.org/3/library/asyncio-task.html
        :return:
        """
        import asyncio
        import datetime
        loop = asyncio.get_running_loop()
        end_time = loop.time() + 5.0
        while True:
            print(datetime.datetime.now())
            if (loop.time() + 1.0) >= end_time:
                break
            await asyncio.sleep(1)
            yield datetime.datetime.now()

    with patch.object(onto.source.kafka, '_kafka_subscribe', _mock_subscribe):
        from onto.source.kafka import KafkaSource
        src = KafkaSource(topic_name='my-topic')
        import asyncio
        loop = asyncio.get_event_loop()
        src.start(loop=loop)

        # import asyncio
        # loop = asyncio.get_event_loop()
        # from starlette.applications import Starlette
        # app = Starlette(debug=True)
        # from uvicorn import Config
        # config = Config(app=app, loop=loop, port=8080, debug=True)
        # from uvicorn import Server
        # server = Server(config)
        # loop.run_until_complete(server.serve())

