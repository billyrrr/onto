import functools

from onto.common import _NA
from onto.database import Database, Reference, Snapshot, Listener
from onto.context import Context as CTX

import kafka

# TODO: NOTE maximum of 1 firestore client allowed since we used a global var.
from typing import List
from onto.query.query import Query
from onto.store.snapshot_container import SnapshotContainer
from math import inf

FirestoreListener = None


class KafkaReference(Reference):

    def is_collection(self):
        return len(self.params) % 2 == 1

    @property
    def collection(self):
        return self.first

    def is_document(self):
        return len(self.params) % 2 == 0

    @classmethod
    def from__document_name(cls, document_name: str):
        return cls.from_str(document_name)

    @property
    def _document_path(self):
        return str(self)


class KafkaDatabase(Database):

    bootstrap_servers = None

    @classmethod
    @functools.lru_cache(maxsize=None)
    def kafka_producer(cls) -> kafka.KafkaProducer:
        from kafka import KafkaProducer
        producer = KafkaProducer(bootstrap_servers=[cls.bootstrap_servers])
        return producer

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA,
            **kwargs):
        d = snapshot.to_dict()
        import json
        s = json.dumps(d)
        b = s.encode(encoding='utf-8')
        bk = ref.id.encode(encoding='utf-8')
        cls.kafka_producer().send(topic=ref.collection, key=bk, value=b, **kwargs)

    update = set
    create = set

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        cls.kafka_producer().send(topic=ref.collection, key=ref.id, value=None)

    ref = KafkaReference()


class KafkaSnapshot(Snapshot):

    @classmethod
    def from_data_and_meta(
            cls, **kwargs):
        """

        :param kwargs:
        :return:
        """
        DATA_KEYWORD = 'data'
        if DATA_KEYWORD not in kwargs:
            raise ValueError
        else:
            data = kwargs[DATA_KEYWORD]
            __onto_meta__ = {
                key: val
                for key, val in kwargs.items()
                if key != DATA_KEYWORD
            }
            return cls(**data, __onto_meta__=__onto_meta__)

    @classmethod
    def empty(cls, **kwargs):
        return cls.from_data_and_meta(
            data=dict(),
            exists=False,
            **kwargs
        )

