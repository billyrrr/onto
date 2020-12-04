from functools import partial
from pathlib import Path
from subprocess import Popen

from pytest_kafka import (
    make_zookeeper_process, make_kafka_server, make_kafka_consumer,
    terminate,
)

from onto.database.kafka import KafkaDatabase


def get_bins():
    from pathlib import Path
    ROOT = Path.cwd()
    KAFKA_SCRIPTS = ROOT / 'kafka/bin/'
    KAFKA_BIN = str(KAFKA_SCRIPTS / 'kafka-server-start.sh')
    ZOOKEEPER_BIN = str(KAFKA_SCRIPTS / 'zookeeper-server-start.sh')
    # You can pass a custom teardown function (or parametrise ours). Just don't call it `teardown`
    # or Pytest will interpret it as a module-scoped teardown function.
    return KAFKA_BIN, ZOOKEEPER_BIN


KAFKA_BIN, ZOOKEEPER_BIN = get_bins()

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
    kafka_server = KafkaProducer(bootstrap_servers='localhost:9092')
    kafka_server.send('my-topic', value='hello world!'.encode('utf-8'))


def test_save_instance(kafka_server):
    # from examples.meeting_room.domain_models import Meeting

    from pony.orm import sql_debug
    from onto.collection_mixin import db
    from pony.orm.dbproviders.sqlite import SQLiteProvider

    import pony.options
    pony.options.CUT_TRACEBACK = False

    from examples.meeting_room.domain_models import Meeting
    # sql_debug(True)  # Output all SQL queries to stdout
    #
    # db.bind(SQLiteProvider, filename=':memory:', create_db=True)
    # db.generate_mapping(check_tables=False, create_tables=True)
    m = Meeting.new(doc_id='mm')
    m.save()
