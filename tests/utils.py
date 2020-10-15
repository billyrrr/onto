import warnings

from google.cloud.firestore import CollectionReference


def _delete_all(CTX, collection_name=None, subcollection_name=None):
    """ For testing purposes only. Use with caution. Never use in production.
            Protection against such use case may fail.

    :param CTX:
    :param collection_name:
    :return:
    """
    testing_datastore = CTX.dbs.firestore
    app_name = CTX.services.firebase.name
    if not app_name.find("testing"):
        raise Exception("Firebase App Name is {}. "
                        "Only app name containing testing is supported"
                        .format(app_name))
    if collection_name is not None:
        collection: CollectionReference = testing_datastore._doc_ref_from_ref(testing_datastore.ref/collection_name)
    elif subcollection_name is not None:
        collection: CollectionReference = testing_datastore._doc_ref_from_ref(testing_datastore.ref/'**'/subcollection_name)

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

    delete_collection(collection, 100)
