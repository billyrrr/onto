""" DocumentMediator listens to change in a single document and triggers
        functions when such document change.
"""
from .document import ViewMediatorDAV as DocumentMediator

""" QueryMediator listens to the result of a query and triggers 
        functions when the result of such query changes. 
"""
from .query_delta import ViewMediatorDeltaDAV as QueryMediator, \
    ProtocolBase, \
    OnSnapshotTasksMixin

""" RestMediator pulls and modifies data when requested with REST API. 
"""
from .rest_api import ViewMediator as RestMediator

""" WsMediator establishes websocket connection with client. 
"""
from .websocket import ViewMediatorWebsocket as WsMediator


class Mediator:

    source = None
    sink = None

    @classmethod
    def start(cls):
        cls.source.start()
