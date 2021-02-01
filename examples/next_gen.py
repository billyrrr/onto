from collections import namedtuple
from datetime import datetime

from onto.domain_model import DomainModel
from onto.models.base import Serializable
from onto import attrs


class UserTime(Serializable):
    time: datetime = attrs.bproperty()
    timestamp = attrs.integer(import_enabled=False)

    @timestamp.getter
    def timestamp(self):
        return self.time.timestamp()


class Location(DomainModel):

    latitude = attrs.bproperty(type_cls=float)
    longitude = attrs.bproperty(type_cls=float)


class RideFailureEvent(DomainModel):

    ride = attrs.relation(dm_cls='RideOrder')


class RideOrder(DomainModel):

    status = attrs.string()
    category = attrs.string()
    create_time = attrs.embed(obj_cls=UserTime)
    start_location = attrs.relation(dm_cls=Location)
    group = attrs.relation(dm_cls='Group')

    def add_group(self, group):
        if not self.has_group():
            self.group = group
        else:
            raise ValueError

    has_group = attrs.bproperty(type_cls=bool)

    @has_group.getter
    def has_group(self):
        return self.group is not None

    def fail_ride(self):
        failure_event = RideFailureEvent.new(ride=self)
        failure_event.save()
        self.status = 'open'


class Group(DomainModel):
    rides = attrs.relation(dm_cls='RideOrder', collection=set)

    def add_ride(self, ride):
        if ride not in self.rides:
            self.rides.add(ride)
        else:
            raise ValueError


class FailureMessage(DomainModel):

    text = attrs.bproperty(type_cls=str)


class JoinRideDirective(DomainModel):
    status = attrs.bproperty(type_cls=str)
    group = attrs.relation(dm_cls='Group')
    ride = attrs.relation(dm_cls='RideOrder')
    exception = attrs.embed()
    message = attrs.relation(dm_cls=FailureMessage, collection=list)

    def execute_new(self):
        try:
            self.group.add_ride(self.ride)
            self.ride.add_group(self.group)
        except:
            self.message = FailureMessage.new(text="Failure")
            self.status = "failed"


class RideTime(DomainModel):

    order = attrs.relation(dm_cls=RideOrder)
    category = attrs.string(import_enabled=False)
    timestamp = attrs.bproperty(type_cls=float)

    @category.getter
    def category(self):
        return self.order.category

    @timestamp.getter
    def timestamp(self):
        return self.order.time.timestamp
