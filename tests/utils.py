import warnings

from google.cloud.firestore import CollectionReference


def _delete_all(CTX, collection_name):
    """ For testing purposes only. Use with caution. Never use in production.
            Protection against such use case may fail.

    :param CTX:
    :param collection_name:
    :return:
    """
    app_name = CTX.firebase_app.name
    if not app_name.find("testing"):
        raise Exception("Firebase App Name is {}. "
                        "Only app name containing testing is supported"
                        .format(app_name))
    event_collection: CollectionReference = CTX.db.collection(collection_name)

    warnings.warn("Deleting collection: {}, App Name: {}.".format(collection_name, app_name))

    def delete_collection(coll_ref, batch_size, doc_limit=10):
        """
        Ref: https://firebase.google.com/docs/firestore/manage-data/delete-data
        :param coll_ref:
        :param batch_size:
        :return:
        """
        docs = coll_ref.limit(doc_limit).get()
        deleted = 0
        docs_count = 0

        for doc in docs:
            docs_count = docs_count + 1
            print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
            doc.reference.delete()
            deleted = deleted + 1

        # Note that this line was "if deleted >= batch_size"
        if deleted < batch_size and docs_count >= doc_limit:
            return delete_collection(coll_ref, batch_size)

    delete_collection(event_collection, 100)
