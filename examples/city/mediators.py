from google.cloud.firestore_v1 import DocumentSnapshot

from examples.city.forms import CityForm
from examples.city.views import CityView
from onto.view.base import ViewMediatorBase
from onto.view_mediator_dav import ViewMediatorDeltaDAV, ProtocolBase


class CityViewMediator(ViewMediatorDeltaDAV):

    def notify(self, obj):
        obj.save()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
            view = CityView.new(snapshot=snapshot)
            mediator.notify(obj=view)


class CityFormMediator(ViewMediatorDeltaDAV):

    def notify(self, obj):
        obj.propagate_change()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator: ViewMediatorBase):
            obj = CityForm.new(doc_ref=snapshot.reference)
            obj.update_vals(with_raw=snapshot.to_dict())
            mediator.notify(obj=obj)
