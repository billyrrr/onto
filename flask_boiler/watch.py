import time

from google.cloud.firestore_v1 import DocumentSnapshot, DocumentReference
from google.cloud.firestore_v1.watch import Watch, WATCH_TARGET_ID, document_watch_comparator


class DataListener:

    def __init__(self, document_refs, snapshot_callback, firestore, once=False):
        """

        :param document_refs: a list of string
        :param snapshot_callback:
        """

        target = {
                "documents": {"documents": document_refs},
                "target_id": WATCH_TARGET_ID,
                "once": once
            }

        def comparator(doc1: DocumentSnapshot, doc2: DocumentSnapshot):
            if doc1.reference._document_path > doc2.reference._document_path:
                return 1
            elif doc1.reference._document_path == doc2.reference._document_path:
                return 0
            else:
                return -1

        self.watch = Watch(document_reference=None,
                           firestore=firestore,
                           target=target,
                           comparator=comparator,
                           snapshot_callback=snapshot_callback,
                           document_snapshot_cls=DocumentSnapshot,
                           document_reference_cls=DocumentReference,
                           )

    def wait_for_once_done(self):
        # TODO: Find a better way
        # TODO: review and test
        # time.sleep(2)
        while not self.watch.has_pushed:
            time.sleep(2)
        # self.watch._consumer._thread.join()

    def __del__(self):
        self.watch.close()
