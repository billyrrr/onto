from google.cloud.firestore_v1 import DocumentSnapshot, Watch, \
    DocumentReference

from flask_boiler.context import Context as CTX
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

    def _get_on_snapshot(self):
        """
        Implement in subclass
        """
        def on_snapshot(snapshots, changes, timestamp):
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
                    CTX.logger.exception(f"DAV failed "
                                         f"for {snapshot.reference.path}")
                else:
                    CTX.logger.info(f"DAV succeeded "
                                    f"for {snapshot.reference.path}")

        return on_snapshot

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


def create_mutation_protocol(mutation):

    class _MutationProtocol:

        @staticmethod
        def on_create(snapshot, mediator):
            mutation.mutate_create(
                doc_id=snapshot.reference.id,
                data=snapshot.to_dict()
            )

    return _MutationProtocol