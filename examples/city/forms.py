from .models import City
from onto.context import Context as CTX
from onto.view_model import ViewModel, Struct
from onto.store import Store, reference
from onto import attrs


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
