# import functools
#
# from onto.common import _NA
# from onto.database import Database, Reference, Snapshot, Listener
# from onto.context import Context as CTX
#
# import kafka
#
# # TODO: NOTE maximum of 1 firestore client allowed since we used a global var.
# from typing import List
# from onto.query.query import Query
# from onto.store.snapshot_container import SnapshotContainer
# from math import inf
#
# FirestoreListener = None
#
#
# class KafkaReference(Reference):
#
#     def is_collection(self):
#         return len(self.params) % 2 == 1
#
#     @property
#     def collection(self):
#         return self.first
#
#     def is_document(self):
#         return len(self.params) % 2 == 0
#
#     @classmethod
#     def from__document_name(cls, document_name: str):
#         return cls.from_str(document_name)
#
#     @property
#     def _document_path(self):
#         return str(self)
#
#
# class KafkaReadDatabase(Database):
#
#     def __init__(self, collection_id: str):
#         self.collection_id = collection_id
#         self.consumer = AIOKafkaConsumer(
#             'my_topic', 'my_other_topic',
#             bootstrap_servers='localhost:9092',
#             group_id="my-group")
#
#     async def start_consumer(self):
#         consumer =
#         # Get cluster layout and join group `my-group`
#         await consumer.start()
#         try:
#             # Consume messages
#             async for msg in consumer:
#                 print("consumed: ", msg.topic, msg.partition, msg.offset,
#                       msg.key, msg.value, msg.timestamp)
#         finally:
#             # Will leave consumer group; perform autocommit if enabled.
#             await consumer.stop()
#
#     async def ensure_timestamp(self, ts):
#         """
#         A helper method to wait for last_poll_timestamp to exceed the timestamp.
#         Used to make sure that all messages are loaded are server is ready.
#         """
#
#
#     @classmethod
#     def listener(cls):
#         from onto.database.utils import GenericListener
#         return GenericListener
#
#     bootstrap_servers = None
#
#     d = dict()
#
#     @classmethod
#     def _onto_set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA):
#         cls.d[str(ref)] = snapshot.to_dict()
#         cls.listener()._pub(reference=ref, snapshot=snapshot)
#
#     @classmethod
#     def get(cls, ref: Reference, transaction=_NA):
#         return Snapshot(cls.d[str(ref)])
#
#     update = set
#     create = set
#
#     @classmethod
#     def delete(cls, ref: Reference, transaction=_NA):
#         """ Note: this only deletes one instance that has _doc_id == ref.last
#
#         :param ref:
#         :param transaction:
#         :return:
#         """
#         del cls.d[str(ref)]
#
#
# class KafkaSnapshot(Snapshot):
#
#     @classmethod
#     def from_data_and_meta(
#             cls, **kwargs):
#         """
#
#         :param kwargs:
#         :return:
#         """
#         DATA_KEYWORD = 'data'
#         if DATA_KEYWORD not in kwargs:
#             raise ValueError
#         else:
#             data = kwargs[DATA_KEYWORD]
#             __onto_meta__ = {
#                 key: val
#                 for key, val in kwargs.items()
#                 if key != DATA_KEYWORD
#             }
#             return cls(**data, __onto_meta__=__onto_meta__)
#
#     @classmethod
#     def empty(cls, **kwargs):
#         return cls.from_data_and_meta(
#             data=dict(),
#             exists=False,
#             **kwargs
#         )
#
