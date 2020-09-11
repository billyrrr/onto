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
kafka_server = make_kafka_server(KAFKA_BIN, 'zookeeper_proc', kafka_port=9092, teardown_fn=teardown_fn)
kafka_consumer = make_kafka_consumer(
    'kafka_server', seek_to_beginning=True, kafka_topics=['topic'])


def test_fixture(kafka_server):
    from kafka import KafkaProducer

    # assert isinstance(kafka_server, KafkaProducer)
    kafka_server = KafkaProducer(bootstrap_servers='localhost:9092', api_version=(0, 10, 1))
    kafka_server.send('my-topic', value='hello world!'.encode('utf-8'))
