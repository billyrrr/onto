from .models import City
from flask_boiler.context import Context as CTX
from flask_boiler.view_model import ViewModel, Struct
from flask_boiler.store import Store, reference
from flask_boiler import attrs


class CityForm(ViewModel):

    name = attrs.bproperty()
    country = attrs.bproperty()
    city_id = attrs.bproperty()

    city = attrs.bproperty(initialize=True)

    @city.init
    def city(self):
        self._attrs.city = City.new(doc_id=self.doc_ref.id)

    @name.setter
    def name(self, val):
        self.city.city_name = val

    @country.setter
    def country(self, val):
        self.city.country = val

    def propagate_change(self):
        self.city.save()
