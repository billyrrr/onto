from google.cloud.firestore_v1 import DocumentSnapshot

from examples.city.views import CityView
from flask_boiler.view_mediator import ViewMediatorBase
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV, ProtocolBase


class CityViewMediator(ViewMediatorDeltaDAV):

    def notify(self, obj):
        obj.save()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
            view = CityView.new(snapshot=snapshot)
            mediator.notify(obj=view)
