"""
Equivalent implementation for flink stateful functions example - ridesharing
ref: https://github.com/apache/flink-statefun/blob/master/statefun-examples/statefun-ridesharing-example/statefun-ridesharing-example-functions/src/main/java/org/apache/flink/statefun/examples/ridesharing/FnDriver.java
"""
from onto.models.base import Serializable

"""
Rewrite callback-style code to async-await: 
ref: https://www.coreycleary.me/how-to-rewrite-a-callback-function-in-promise-form-and-async-await-form-in-javascript 
"""

from onto.domain_model import DomainModel
from onto.attrs import attrs


class RideshareBase(DomainModel):
    pass


class Passenger(RideshareBase):

    async def request_ride(self, start_geo_cell, end_geo_cell):
        r = Ride.create()  # TODO: implement create
        await r.passenger_joins(
            passenger=self,
            start_geo_cell=start_geo_cell,
            end_geo_cell=end_geo_cell
        )

    class PassengerMessage(DomainModel):
        passenger = attrs.relation('Passenger')

        class RideFailedMessage(Serializable):
            ride = attrs.relation('Ride')

        ride_failed = attrs.embed(RideFailedMessage).optional

        class DriverHasBeenFoundMessage(Serializable):
            driver = attrs.relation('Driver')
            driver_geo_cell = attrs.relation('GeoCell')

        driver_found = attrs.embed(RideFailedMessage).optional

        class RideHasStarted(Serializable):
            driver = attrs.relation('Driver')

        ride_started = attrs.embed(RideHasStarted).optional

        class RideHasEnded(Serializable):
            pass  # TODO: make sure that empty class works

        ride_ended = attrs.embed(RideHasEnded).optional

    async def ride_failed(self, ride: 'Ride'):
        message = self.PassengerMessage.new(
            passenger=self,
            ride_failed=self.PassengerMessage.RideFailedMessage.new(
                ride=ride
            )
        )
        message.save()

    async def driver_joins_ride(self, driver: 'Driver', driver_geo_cell: 'GeoCell'):
        message = self.PassengerMessage.new(
            passenger=self,
            driver_found=self.PassengerMessage.DriverHasBeenFoundMessage.new(
                driver=driver,
                driver_geo_cell=driver_geo_cell
            )
        )
        message.save()

    async def ride_started(self, driver: 'Driver'):
        message = self.PassengerMessage.new(
            passenger=self,
            ride_started=self.PassengerMessage.RideHasStarted.new(
                driver=driver
            )
        )
        message.save()

    async def ride_ended(self):
        message = self.PassengerMessage.new(
            passenger=self,
            ride_started=self.PassengerMessage.RideHasEnded.new()
        )
        message.save()


class DriverRejectsPickupError(RideshareBase, Exception):
    driver = attrs.relation(dm_cls='Driver')
    ride = attrs.relation(dm_cls='Ride')


class Driver(RideshareBase):
    is_taken: bool = attrs.required
    current_ride = attrs.relation(dm_cls='Ride').optional
    current_location: 'GeoCell' = attrs.relation(dm_cls='GeoCell')

    @is_taken.getter
    def is_taken(self):
        # TODO: make better
        return self.current_ride is not None

    async def pickup_passenger(self, ride: 'Ride', passenger: Passenger,
                passenger_start_cell: 'GeoCell',
                passenger_end_cell: 'GeoCell'):
        if self.is_taken:
            raise DriverRejectsPickupError(driver=self, ride=ride)
        self.current_ride = ride

        # "    // We also need to unregister ourselves from the current geo cell we belong to."
        if geo_cell := self.current_location:
            await geo_cell.leave_cell(driver=self)

        await ride.driver_joins(driver=self, driver_location=self.current_location)

        message = self.DriverMessage.new(
            driver=self,
            pickup_passenger=self.DriverMessage.PickupPassengerMessage.new(
                passenger=passenger,
                start_geo_location=passenger_start_cell,
                end_geo_location=passenger_end_cell
            )
        )
        message.save()

    class DriverMessage(RideshareBase):
        driver = attrs.relation('Driver')

        class PickupPassengerMessage(Serializable):
            ride = attrs.relation('Ride')  # TODO: maybe passenger_id
            start_geo_location = attrs.relation('GeoCell')
            end_geo_location = attrs.relation('GeoCell')

        pickup_passenger = attrs.embed(PickupPassengerMessage)

    async def ride_has_started(self):
        await self.current_ride.ride_started(driver=self, driver_geo_cell=self.current_location)

    async def ride_has_ended(self):
        await self.current_ride.ride_ended()

    async def location_is_updated(self, current_geo_cell: 'GeoCell'):
        # TODO: maybe switch to embed:     final int updated = locationUpdate.getLocationUpdate().getCurrentGeoCell();
        updated = current_geo_cell
        last = self.current_location
        if last is None:
            self.current_location = updated
            await updated.join_cell()
            return
        elif last == updated:
            return
        else:
            self.current_location = updated


class Ride(RideshareBase):
    passenger = attrs.relation(dm_cls=Passenger)
    driver = attrs.relation(dm_cls=Driver)

    async def ride_started(self, driver: Driver, driver_geo_cell: 'GeoCell'):
        await self.passenger.ride_started(driver=driver)

    async def passenger_joins(
            self,
            passenger: Passenger,
            start_geo_cell: 'GeoCell',
            end_geo_cell: 'GeoCell'
    ):
        self.passenger = passenger
        MAX_RETRY = 5
        # Ref: https://stackoverflow.com/a/7663441
        for trial in range(MAX_RETRY):
            if driver := start_geo_cell.get_driver():
                try:
                    await driver.pickup_passenger(
                        ride=self,
                        passenger=passenger,
                        passenger_start_cell=start_geo_cell,
                        passenger_end_cell=end_geo_cell
                    )
                except DriverRejectsPickupError as _:
                    # TODO: NOTE difference from java impl
                    """
                    final int startGeoCell = passenger.get().getStartGeoCell();
                    String cellKey = String.valueOf(startGeoCell);
                    context.send(FnGeoCell.TYPE, cellKey, GetDriver.getDefaultInstance());
                    """
                    continue  # to retry
                else:
                    break
        else:
            await passenger.ride_failed(ride=self)

    async def driver_joins(self, driver, driver_location):
        self.driver = driver
        await self.passenger.driver_joins_ride(driver=driver, driver_geo_cell=driver_location)

    async def ride_ended(self, ):
        await self.passenger.ride_ended()
        self.passenger = None
        self.driver = None


class GeoCell(RideshareBase):

    drivers: list = attrs.list(
        value=attrs.relation(dm_cls=Driver)
    )

    async def get_driver(self) -> Driver:
        if len(self.drivers) != 0:
            next_driver = self.drivers[0]
            return next_driver
        else:
            return None

    async def leave_cell(self, driver: Driver):
        self.drivers.remove(driver)

    async def add_driver(self):
        # TODO: mutated local variable vs mutated instance state;
        #  may cause difference in behavior
        if self.drivers is None:
            self.drivers = list()
        self.drivers.append(Driver)

    join_cell = add_driver



