from .models import City
from flask_boiler.context import Context as CTX
from flask_boiler.view_model import ViewModel, Struct
from flask_boiler.store import Store, reference
from flask_boiler import attrs


class CityStore(Store):
    city = reference(many=False)


class CityView(ViewModel):

    name = attrs.bproperty()
    country = attrs.bproperty()

    @classmethod
    def new(cls, snapshot):
        store = CityStore()
        store.add_snapshot("city", dm_cls=City, snapshot=snapshot)
        store.refresh()
        return cls(store=store)

    @name.getter
    def name(self):
        return self.store.city.city_name

    @country.getter
    def country(self):
        return self.store.city.country

    @property
    def doc_ref(self):
        return CTX.db.document(f"cityView/{self.store.city.doc_id}")
