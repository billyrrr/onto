from flask_boiler.domain_model import DomainModel
from flask_boiler import attrs


class City(DomainModel):

    city_name = attrs.bproperty()
    country = attrs.bproperty()
    capital = attrs.bproperty()

    class Meta:
        collection_name = "City"


class Municipality(City):
    pass


class StandardCity(City):
    city_state = attrs.bproperty()
    regions = attrs.bproperty()
