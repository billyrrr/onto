import asyncio
import functools
from threading import Thread
from queue import Queue
from typing import Optional, Awaitable

from google.cloud.firestore_v1 import DocumentSnapshot, Watch, \
    DocumentReference
from google.cloud.firestore_v1.watch import DocumentChange

from flask_boiler.context import Context as CTX
from flask_boiler.query import run_transaction
from flask_boiler.view.base import ViewMediatorBase


class ViewMediatorDeltaDAV(ViewMediatorBase):

    def notify(self, obj):
        """ Called when the object has state changes to be notified.

        :param obj: the object with state change
        :return:
        """
        obj.save()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "Protocol"):
            raise NotImplementedError

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

    def _on_snapshot(self, snapshots, changes, timestamp):
        """
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

        """

        query, on_snapshot = self.query, self._get_on_snapshot()

        watch = Watch.for_query(
            query=query,
            snapshot_callback=on_snapshot,
            snapshot_class_instance=DocumentSnapshot,
            reference_class_instance=DocumentReference
        )


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


class OnSnapshotTasksMixin:
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
            item()
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
            if snapshot.update_time == snapshot.create_time:
                f = functools.partial(mediator.on_post, snapshot=snapshot)
            else:
                f = functools.partial(mediator.on_patch, snapshot=snapshot)
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
            before_snapshot: Optional[DocumentSnapshot]=None,
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


def create_mutation_protocol(mutation):

    class _MutationProtocol:

        @staticmethod
        def on_create(snapshot, mediator):
            mutation.mutate_create(
                doc_id=snapshot.reference.id,
                data=snapshot.to_dict()
            )

    return _MutationProtocol