import asyncio
import functools
from threading import Thread
from queue import Queue
from typing import Optional, Awaitable

from google.cloud.firestore_v1 import DocumentSnapshot, Watch, \
    DocumentReference

from onto import sink
from onto.watch import DocumentChange

from onto.context import Context as CTX
# # https://dev.to/googlecloud/portable-cloud-functions-with-the-python-functions-framework-a6a
# from google.cloud.functions.context import Context as GcfContext

from onto.query import run_transaction
from onto.view.base import ViewMediatorBase

# NOTE: note for deploying to cloud functions
# NOTE: gcloud functions deploy to_trigger --runtime python37 --trigger-event providers/cloud.firestore/eventTypes/document.create --trigger-resource "projects/flask-boiler-testing/databases/(default)/documents/gcfTest/{gcfTestDocId}"
# NOTE: No to unauthenticated invocations
from onto.watch import DataListener

EVENT_TYPE_MAPPING = dict(
    create="providers/cloud.firestore/eventTypes/document.create",
    update="providers/cloud.firestore/eventTypes/document.update",
    delete="providers/cloud.firestore/eventTypes/document.delete",
    write="providers/cloud.firestore/eventTypes/document.write"
)


class DeltaSink(sink.firestore):

    def emit(self, doc_ref, obj):
        doc_ref.save(obj.to_dict())


class ViewMediatorDeltaDAV(ViewMediatorBase):

    def notify(self, obj):
        """ Called when the object has state changes to be notified.

        :param obj: the object with state change
        :return:
        """
        self.sink.emit(obj.doc_ref, obj)

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     if not hasattr(cls, "Protocol"):
    #         raise NotImplementedError

    def __init__(self, *args, query, **kwargs):
        """ Initializes a ViewMediator to declare protocols that
                are called when the results of a query change. Note that
                mediator.start must be called later.

        :param args:
        :param query: a listener will be attached to this query
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.query = query
        self.sink = DeltaSink()

    def _on_snapshot(self, snapshots, changes, timestamp):
        """ For use with
        Note that server reboot will result in some "Modified" objects
            to be routed as "Added" objects

        :param snapshots:
        :param changes:
        :param timestamp:
        """
        for change in changes:
            snapshot = change.document
            assert isinstance(snapshot, DocumentSnapshot)
            try:
                CTX.logger.info(f"DAV: {self.__class__.__name__} started "
                                f"for {snapshot.reference.path}")
                if change.type.name == 'ADDED':
                    self.Protocol.on_create(
                        snapshot=snapshot,
                        mediator=self
                    )
                elif change.type.name == 'MODIFIED':
                    self.Protocol.on_update(
                        snapshot=snapshot,
                        mediator=self
                    )
                elif change.type.name == 'REMOVED':
                    self.Protocol.on_delete(
                        snapshot=snapshot,
                        mediator=self
                    )
            except Exception as e:
                """
                Expects e to be printed to the logger 
                """
                CTX.logger.exception(f"DAV {self.__class__.__name__} failed "
                                     f"for {snapshot.reference.path}")
            else:
                CTX.logger.info(f"DAV {self.__class__.__name__} succeeded "
                                f"or enqueued "
                                f"for {snapshot.reference.path}")

    def _get_on_snapshot(self):
        return self._on_snapshot

    def start(self):
        """ Starts a listener to the query.
        Do not use this for cloud functions.

        """

        query, on_snapshot = self.query, self._get_on_snapshot()

        self.listener = DataListener(snapshot_callback=on_snapshot,
                         firestore=CTX.db, once=False, query=query)


class ProtocolBase:
    """ Protocol to specify actions when a document is 'ADDED', 'MODIFIED', and
            'REMOVED'.

    """

    @staticmethod
    def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
        """
        Called when a document is 'ADDED' to the result of a query.

        :param snapshot: Firestore Snapshot added
        :param mediator: ViewMediator object
        """
        pass

    @staticmethod
    def on_update(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
        """ Called when a document is 'MODIFIED' in the result of a query.

        :param snapshot: Firestore Snapshot modified
        :param mediator: ViewMediator object
        """
        pass

    @staticmethod
    def on_delete(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
        """ Called when a document is 'REMOVED' in the result of a query.

        :param snapshot: Firestore Snapshot deleted
        :param mediator: ViewMediator object
        :return:
        """
        pass


class OnTriggerMixin:
    TRIGGER_EVENT_TYPE: str = "providers/cloud.firestore/eventTypes/document.write"

    def __init__(self, *args, resource_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        if resource_path is not None:
            self.resource = "projects/" + CTX.config.APP_NAME + "/databases/(default)/documents/" + resource_path

    def _on_trigger(self, data, context):
        """ For use with Cloud Functions

        :return:
        """
        event_type = context.event_type
        if event_type == EVENT_TYPE_MAPPING['create']:
            snapshot = make_snapshot(data['value'], client=CTX.db)
            self.on_post(snapshot=snapshot)
        elif event_type == EVENT_TYPE_MAPPING['update']:
            before_snapshot = make_snapshot(data['oldValue'], client=CTX.db)
            after_snapshot = make_snapshot(data['value'], client=CTX.db)
            self.on_patch(
                after_snapshot=after_snapshot,
                before_snapshot=before_snapshot)
        elif event_type == EVENT_TYPE_MAPPING['delete']:
            before_snapshot = make_snapshot(data['oldValue'], client=CTX.db)
            self.on_remove(snapshot=before_snapshot)
        elif event_type == EVENT_TYPE_MAPPING['write']:
            before_snapshot = make_snapshot(data['oldValue'], client=CTX.db)
            after_snapshot = make_snapshot(data['value'], client=CTX.db)
            if before_snapshot is None and after_snapshot is not None:
                self.on_post(snapshot=after_snapshot)
            elif before_snapshot is not None and after_snapshot is not None:
                self.on_patch(
                    after_snapshot=after_snapshot,
                    before_snapshot=before_snapshot)
            elif before_snapshot is not None and after_snapshot is None:
                self.on_remove(snapshot=before_snapshot)
            else:
                CTX.logger.error(
                    f"flask-boiler failed to route for: {data} {context}")
                raise ValueError
        else:
            #  TODO: implement mapping for 'write'
            CTX.logger.error(
                msg=f"event_type not supported. {data} {context}")

    def __call__(self, *args, **kwargs):
        try:
            return self._on_trigger(*args, **kwargs)
        except Exception as e:
            CTX.logger.exception(msg="trigger failed")


class OnSnapshotTasksMixin(OnTriggerMixin):
    """
    To be added before ViewModel

    TODO: check contextvar CTX.transaction context switching during
        an await in async function.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = Queue()

    def start(self, *args, **kwargs):
        self._start_thread()
        super().start(*args, **kwargs)

    def _main(self):
        """ Push None to self.q to stop the thread

        :return:
        """
        while True:
            item = self.q.get()
            if item is None:
                break
            try:
                item()
            except Exception as e:
                CTX.logger.exception(f"a task in the queue has failed {item}")
            self.q.task_done()

    def _start_thread(self):
        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def _add_awaitable(self, item):
        """ TODO: test

        :param item:
        :return:
        """
        self.q.put(item)

    def _on_snapshot(self, snapshots, changes, timestamp):
        """
        Note that server reboot will result in some "Modified" objects
            to be routed as "Added" objects

        :param snapshots:
        :param changes:
        :param timestamp:
        """
        for change in changes:
            assert isinstance(change, DocumentChange)
            snapshot = change.document
            assert isinstance(snapshot, DocumentSnapshot)
            try:
                CTX.logger.info(f"DAV: {self.__class__.__name__} started "
                                f"for {snapshot.reference.path}")
                if change.type.name == 'ADDED':
                    self.Protocol.on_create(
                        snapshot=snapshot,
                        mediator=self
                    )
                elif change.type.name == 'MODIFIED':
                    if change.old_index != -1:
                        # Append before snapshot if available
                        before_snapshot = snapshots[change.old_index]
                    else:
                        before_snapshot = None
                    after_snapshot = snapshots[change.new_index]
                    self.on_patch(after_snapshot=after_snapshot,
                                  before_snapshot=before_snapshot)
                elif change.type.name == 'REMOVED':
                    self.Protocol.on_delete(
                        snapshot=snapshot,
                        mediator=self
                    )
            except Exception as e:
                """
                Expects e to be printed to the logger 
                """
                CTX.logger.exception(f"DAV {self.__class__.__name__} failed "
                                     f"for {snapshot.reference.path}")
            else:
                CTX.logger.info(f"DAV {self.__class__.__name__} succeeded "
                                f"or enqueued "
                                f"for {snapshot.reference.path}")

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            # if snapshot.update_time == snapshot.create_time:
            f = functools.partial(mediator.on_post, snapshot=snapshot)
            # else:
            #     f = functools.partial(mediator.on_patch, after_snapshot=snapshot)
            mediator._add_awaitable(f)

        @staticmethod
        def on_update(snapshot: DocumentSnapshot, mediator):
            f = functools.partial(mediator.on_patch, snapshot=snapshot)
            mediator._add_awaitable(f)

        @staticmethod
        def on_delete(snapshot: DocumentSnapshot, mediator):
            f = functools.partial(mediator.on_remove, snapshot=snapshot)
            mediator._add_awaitable(f)

    def on_post(self, snapshot: DocumentSnapshot):
        """
        Called when a document is 'ADDED' to the result of a query.
        (Will be enqueued to a different thread and run concurrently)

        :param snapshot: Firestore Snapshot added
        """
        pass

    def on_patch(
            self,
            after_snapshot: DocumentSnapshot,
            before_snapshot: Optional[DocumentSnapshot] = None,
    ):
        """ Called when a document is 'MODIFIED' in the result of a query.
        (Will be enqueued to a different thread and run concurrently)

        :param after_snapshot:
        :param before_snapshot: May be None if timestamp set to watcher
            is later than the last_updated time of a snapshot
        :return:
        """
        pass

    def on_remove(self, snapshot: DocumentSnapshot):
        """ Called when a document is 'REMOVED' in the result of a query.
        (Will be enqueued to a different thread and run concurrently)

        :param snapshot: Firestore Snapshot deleted
        """
        pass


def make_snapshot(value, client) -> Optional[DocumentSnapshot]:
    """ Converts a json representation of Document protobuf to DocumentSnapshot
    TODO: note that this method uses _helpers and other internal methods
    TODO: of google cloud library


    :param value:
    :param client:
    :return:
    """

    # Ref: https://developers.google.com/protocol-buffers/docs/pythontutorial
    if value == dict():
        return None

    from google.protobuf.json_format import ParseDict
    from google.cloud.firestore_v1.proto.document_pb2 import Document
    from google.cloud.firestore_v1 import _helpers

    # value is a deserialized (json) form of "Document" protobuf message
    document_pb = ParseDict(value, Document())

    exists = True
    create_time = document_pb.create_time
    update_time = document_pb.update_time
    reference = client.document(document_pb.name)
    data = _helpers.decode_dict(document_pb.fields, client)

    snapshot = DocumentSnapshot(
        reference=reference,
        data=data,
        exists=exists,
        read_time=None,  # No server read_time available
        create_time=create_time,
        update_time=update_time,
    )

    return snapshot


def create_mutation_protocol(mutation):
    class _MutationProtocol:

        @staticmethod
        def on_create(snapshot, mediator):
            mutation.mutate_create(
                doc_id=snapshot.reference.id,
                data=snapshot.to_dict()
            )

    return _MutationProtocol
