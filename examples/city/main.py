from .mediators import CityViewMediator
from .models import City

city_view_mediator = CityViewMediator(
    query=City.get_query()
)

if __name__ == "__main__":
    city_view_mediator.start()
