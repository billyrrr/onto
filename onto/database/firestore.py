import functools

from onto.common import _NA
from onto.database import Database, Reference, Snapshot, Listener
from onto.context import Context as CTX

from google.cloud import firestore
from google.cloud.firestore_v1.document import _get_document_path, \
    DocumentReference, DocumentSnapshot

# TODO: NOTE maximum of 1 firestore client allowed since we used a global var.
from typing import List
from onto.query.query import Query
from onto.store.snapshot_container import SnapshotContainer
from math import inf


FirestoreListener = None

class FirestoreReference(Reference):

    def is_collection(self):
        return len(self.params) % 2 == 1

    @property
    def collection(self):
        return self.first

    def is_document(self):
        return len(self.params) % 2 == 0

    def is_collection_group(self):
        return self.first == "**" and len(self.params) == 2

    @classmethod
    def from__document_name(cls, document_name: str):
        return cls.from_str(document_name)

    @classmethod
    def from_document_reference(cls, ref: DocumentReference):
        return cls.from_str(ref.path)

    @property
    def _document_path(self):
        return str(self)


class FirestoreDatabase(Database):

    firestore_client = None

    @classmethod
    def listener(cls):
        return FirestoreListener


    class Comparators(Database.Comparators):

        eq = '=='
        gt = '>'
        ge = '>='
        lt = '<'
        le = '<='
        contains = 'array_contains'
        _in = 'in'

    @classmethod
    def make_document_path(cls, ref: FirestoreReference):
        """Create and cache the full path for this document.

        Migrated from google.cloud.DocumentReference.document:
            - changed to read document name from ref.path or str(ref)

        Of the form:

            ``projects/{project_id}/databases/{database_id}/...
                  documents/{document_path}``

        Returns:
            str: The full document path.

        Raises:
            ValueError: If the current document reference has no ``client``.
        """
        _document_path_internal = _get_document_path(
            cls.firestore_client,
            ref.path
        )
        return _document_path_internal

    @classmethod
    def transaction(cls):
        return cls.firestore_client.transaction()

    @classmethod
    def _doc_ref_from_ref(cls, ref):
        if ref._is_empty:
            # TODO: change this behavior
            return cls.firestore_client
        elif ref.is_collection_group():
            return cls.firestore_client.collection_group(ref.last)
        elif ref.is_collection():
            return cls.firestore_client.collection(str(ref))
        elif ref.is_document():
            return cls.firestore_client.document(str(ref))
        else:
            raise ValueError

    @classmethod
    def set(cls, ref: Reference, snapshot: Snapshot, transaction=_NA, **kwargs):

        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        doc_ref = cls._doc_ref_from_ref(ref)
        # doc_ref.set(
        #     document_data=snapshot.to_dict()
        # )

        if transaction is None:
            doc_ref.set(document_data=snapshot.to_dict(), **kwargs)
        else:
            transaction.set(reference=doc_ref,
                            document_data=snapshot.to_dict(), **kwargs)

    @classmethod
    def get(cls, ref: Reference, transaction=_NA):
        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        doc_ref = cls._doc_ref_from_ref(ref)

        if transaction is None:
            document_snapshot = doc_ref.get()
        else:
            document_snapshot = doc_ref.get(transaction=transaction)

        return FirestoreSnapshot.from_document_snapshot(
            document_snapshot=document_snapshot)

    @classmethod
    def get_many(cls, refs: [Reference], transaction=_NA):
        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        doc_refs = [cls._doc_ref_from_ref(ref) for ref in refs]

        if transaction is None:
            document_snapshots = cls.firestore_client.get_all(doc_refs)
        else:
            document_snapshots = cls.firestore_client.get_all(
                doc_refs, transaction=transaction)

        for document_snapshot in document_snapshots:
            yield FirestoreReference.from_document_reference(document_snapshot.reference),\
                  FirestoreSnapshot.from_document_snapshot(
                document_snapshot=document_snapshot)

    update = set
    create = set

    @classmethod
    def delete(cls, ref: Reference, transaction=_NA):
        doc_ref = cls._doc_ref_from_ref(ref)
        if transaction is _NA:
            transaction = CTX.transaction_var.get()

        if transaction is None:
            doc_ref.delete()
        else:
            transaction.delete(reference=doc_ref)

    @classmethod
    def query(cls, q: Query):
        for document in q._to_firestore_query().stream():
            assert isinstance(document, DocumentSnapshot)
            ref = FirestoreReference.from_document_reference(document.reference)
            snapshot = FirestoreSnapshot.from_document_snapshot(document)
            yield (ref, snapshot)

    ref = FirestoreReference()


class FirestoreSnapshot(Snapshot):

    @classmethod
    def from_document_snapshot(
            cls, document_snapshot: firestore.DocumentSnapshot):
        return cls(
            document_snapshot.to_dict()
        )

    @classmethod
    def from_data_and_meta(
            cls, **kwargs):
        """ Usage: snapshot = FirestoreSnapshot.from_data_and_meta(
                    # reference=document_ref,
                    data=data,
                    exists=True,
                    read_time=None,
                    create_time=document.create_time,
                    update_time=document.update_time,
                )

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


from threading import Lock, Condition
import heapq


TARGET_ID_RANGE = (32, 64)


class TargetIdAssigner:
    """
    For now, we allow 32 concurrent targets to test that overflow is handled.
    """

    def __init__(self):
        self.lock = Lock()
        self.sold_out = Condition()
        with self.lock, self.sold_out:
            self._heap = list(range(*TARGET_ID_RANGE))
            heapq.heapify(self._heap)

    def assign_id(self):
        with self.lock, self.sold_out:
            while not len(self._heap) > 0:
                self.sold_out.wait()
            item = heapq.heappop(self._heap)
            return item

    def release_id(self, _id):
        with self.lock, self.sold_out:
            heapq.heappush(self._heap, _id)
            self.sold_out.notify(n=1)


_LOGGER = CTX.logger


from _collections import defaultdict


"""
5 changes:
- Just tracked (previously may exist or not have existed in the datastore)
- Just created (previously did not exist in the datastore) 
- Just removed (conditions does not meet query, but was tracked)
- Just deleted (previously tracked and now deleted)
- Just changed (previously tracked and now updated) 

Each listener acts like an airport surveillance radar.
Each aircraft is like a snapshot with its states. 
 
When the flight enters the area, it is first observed by the listener 
    1. the flight may have departed a long time ago and was just observed when 
    passing through the area ("just tracked"), 
        - State of last snapshot is unknown 
    2. or it could have just taken off, and we need to register the flight 
    as a recently departed flight ("just created")
        - State of last snapshot does not exist 
When the flight is no longer observed by the radar, 
    1. the flight may have just landed, in which case, we need to register 
    the flight as landed ("just deleted")
        - New state does not exist 
    2. the flight may have left the area of observation ("just removed")
        - New state is unknown 
When the flight was already observed by the radar (made initial appearance), 
    1. the flight has changed altitude, in which case, we want to run checking 
    to see if the altitude is safe ("just changed")
        - Previous and new state exist 
    
Depending on the time that the radar was turned on, we may observe the same 
signal as "just created" or "just tracked". We are able to see if the flight 
was just created by checking its create and update timestamp. 

"""


def timestamp_key(t) -> tuple:
    return (t.seconds, t.nanos)


class FirestoreListener(Listener):

    _watch = None
    _containers = defaultdict(SnapshotContainer)

    @classmethod
    def _get_watch(cls):

        from onto.context import Context as CTX
        from onto.watch import _Watch

        cls._watch = _Watch(
            # document_reference=None,
            firestore=CTX.db.firestore_client,
            comparator=lambda d1, d2: 1,
            document_snapshot_cls=DocumentSnapshot,
            document_reference_cls=DocumentReference,
        )

        while not cls._watch._rpc.is_active:
            # TODO: change; This is a temporary impl; wait may never stop
            import time
            time.sleep(0.020)

        return cls._watch

    _assigner = TargetIdAssigner()

    @classmethod
    def register(cls, query, source):
        def callback(*args, **kwargs):
            f = functools.partial(source._call, *args, **kwargs)
            cls._coordinator._add_awaitable(f)
        target_id = cls.for_query(query=query, cb=callback)
        cls._registry[target_id] = source

    @classmethod
    def deregister(cls):
        raise NotImplementedError

    @classmethod
    def _process_proto(cls, target_id, proto):
        """

        This method is ported from from google.cloud.firestore_v1.watch

        Copy of the license of google.cloud.firestore_v1.watch:
        # Copyright 2017 Google LLC All rights reserved.
        #
        # Licensed under the Apache License, Version 2.0 (the "License");
        # you may not use this file except in compliance with the License.
        # You may obtain a copy of the License at
        #
        #     http://www.apache.org/licenses/LICENSE-2.0
        #
        # Unless required by applicable law or agreed to in writing, software
        # distributed under the License is distributed on an "AS IS" BASIS,
        # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        # See the License for the specific language governing permissions and
        # limitations under the License.

        Difference from source code: the way document_change is stored

        :param proto:
        :param target_id:
        :return:
        """

        container = cls._containers[target_id]

        _firestore = CTX.db.firestore_client

        document_change = getattr(proto, "document_change", "")
        document_delete = getattr(proto, "document_delete", "")
        # document_remove = getattr(proto, "document_remove", "")
        # filter_ = getattr(proto, "filter", "")

        if str(document_change):
            _LOGGER.debug("on_snapshot: document change")

            # No other target_ids can show up here, but we still need to see
            # if the targetId was in the added list or removed list.
            target_ids = document_change.target_ids or []
            removed_target_ids = document_change.removed_target_ids or []
            changed = False
            removed = False

            if target_id in target_ids:
                changed = True

            if target_id in removed_target_ids:
                removed = True

            if changed:
                _LOGGER.debug("on_snapshot: document change: CHANGED")

                # google.cloud.firestore_v1.types.Document
                document = document_change.document
                # TODO: change
                from google.cloud.firestore_v1 import _helpers
                data = _helpers.decode_dict(document.fields, _firestore)

                # Create a snapshot. As Document and Query objects can be
                # passed we need to get a Document Reference in a more manual
                # fashion than self._document_reference
                document_name = document.name

                document_name = cls._trim_document_name(_firestore,
                                                       document_name)

                ref = FirestoreReference.from__document_name(document_name)

                snapshot = FirestoreSnapshot.from_data_and_meta(
                    # reference=document_ref,
                    data=data,
                    exists=True,
                    read_time=None,
                    create_time=document.create_time,
                    update_time=document.update_time,
                )

                # TODO: apply lock
                if not container.has_previous(ref):
                    container.set(
                        key=ref,
                        val=FirestoreSnapshot.empty(
                            create_time=-inf,
                            update_time=-inf,
                            read_time=-inf
                        ),
                        timestamp=(-inf, -inf)
                    )

                prev = container.previous(ref)
                prev.next = snapshot
                snapshot.prev = prev

                container.set(
                    key=ref,
                    val=snapshot,
                    timestamp=timestamp_key(document.update_time)
                )

            elif removed:
                raise NotImplementedError

        elif str(document_delete):
            _LOGGER.debug("on_snapshot: document change: DELETE")
            name = document_delete.document  # should be a str

            document_name = cls._trim_document_name(_firestore, name)
            ref = FirestoreReference.from__document_name(document_name)

            snapshot = FirestoreSnapshot.empty(
                    create_time=None,
                    update_time=None,
                    read_time=document_delete.read_time
            )

            prev = container.previous(ref)
            prev.next = snapshot
            snapshot.prev = prev

            container.set(
                key=ref,
                val=snapshot,
                timestamp=timestamp_key(document_delete.read_time)
            )
        else:
            raise ValueError  # TODO: implement

    @classmethod
    def _trim_document_name(cls, _firestore, document_name):
        db_str = _firestore._database_string
        db_str_documents = db_str + "/documents/"
        if document_name.startswith(db_str_documents):
            document_name = document_name[len(db_str_documents):]
        return document_name

    @classmethod
    def callback(cls, target_id, protos, read_time, *, cb):
        container = cls._containers[target_id]
        with container.lock:
            for proto in protos:
                cls._process_proto(target_id, proto)
            container._read_times.append(
                (read_time.seconds, read_time.nanos)
            )
            cb(container)

    @classmethod
    def for_query(cls, query: Query, cb):
        query = query._to_firestore_query()
        parent_path, _ = query._parent._parent_info()
        from google.cloud.firestore_v1.proto import firestore_pb2
        query_target = firestore_pb2.Target.QueryTarget(
            parent=parent_path, structured_query=query._to_protobuf()
        )

        target_id = cls._assigner.assign_id()
        target = {
            "query": query_target,
            "target_id": target_id
        }
        import functools
        cls._get_watch().add_target(
            target, functools.partial(cls.callback, cb=cb)
        )

        return target_id

    @classmethod
    def for_refs(cls, refs: List[FirestoreReference], cb):
        documents = [FirestoreDatabase.make_document_path(ref) for ref in refs]
        target_id = cls._assigner.assign_id()
        target = {
            "documents": {"documents": documents},
            "target_id": target_id,
        }
        import functools
        cls._get_watch().add_target(
            target, functools.partial(cls.callback, cb=cb)
        )
        return target_id

    @classmethod
    def release_target(cls, target_id):
        cls._watch.remove_target(target_id)
