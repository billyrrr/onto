from celery import Task
from flasgger import SwaggerView
from flask import request
from google.cloud.firestore import DocumentSnapshot

from onto.context import Context as CTX


def _retrofit(view: SwaggerView, collection_path: str):
    """ Registers a resource so that it is stored in Firestore.

    :return:
    """
    t: Task = CTX.celery_app.task(_pull)
    t.run(view=view, collection_path=collection_path)
    # CTX.celery_app.add_periodic_task(
    #     schedule=1.0,
    #     sig=t
    # )


def _pull(view: SwaggerView, collection_path: str):
    """ Stores REST API response in Firestore.

    :return:
    """
    res = view.get()
    collection = CTX.db.collection(collection_path)
    for key, val in res.items():
        collection.document(document_id=key).set(document_data=val)


def _clear(collection_path: str):
    """ Deletes everything in a collection. USE CAREFULLY!
    NOTE that production release will NOT include this function.

    :param collection_path:
    :return:
    """
    collection = CTX.db.collection(collection_path)
    for doc in collection.stream():
        assert isinstance(doc, DocumentSnapshot)
        doc.reference.delete()

