from .mediators import CityViewMediator, CityFormMediator
from .models import City
from . import CTX

city_view_mediator = CityViewMediator(
    query=City.get_query()
)

city_form_mediator = CityFormMediator(
    query=CTX.db.collection_group("cityForms")
)

if __name__ == "__main__":
    city_view_mediator.start()
    city_form_mediator.start()
