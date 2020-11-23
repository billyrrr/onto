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


class RideOrder(DomainModel):

    category = attrs.string()
    create_time = attrs.embed(obj_cls=UserTime)
    start_location = attrs.relation(dm_cls=Location)


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


_window = namedtuple('_window', ['lo_excl', 'lo_incl', 'hi_excl', 'hi_incl'])


class Window:

    class now:
        pass

    @classmethod
    def last(cls, *, hour=None):
        return _window(lo_incl=cls.now-hour*3600, high_excl=cls.now)

from pony.orm import avg

class GlobalRideTime(DomainModel):
    """
    We should know that ride time is in poisson distribution
    """

    earlier = Window.now - 3600
    later = Window.now

    @property
    def ride_times(self):
        for rt in RideTime:
            if self.earlier < rt.timestamp <= self.later :
                yield rt

    ts = attrs.bproperty(type_cls=float, collection=list)
    @ts.getter
    def ts(self):
        for rt in self.ride_times:
            yield rt.timestamp - self.earlier

    mean = attrs.bproperty(type_cls=float)
    @mean.getter
    def mean(self):
        return avg(self.ts)

    def poisson_dist(self):
        """

        :return:
            a: lambda value in poisson distribution,
            pvalue: confidence value that the data follows a poisson process
        """
        from scipy.stats import gamma, kstest
        a, floc, scale = gamma.fit(
            self.ts,
            fscale=(self.later-self.earlier),
            floc=self.earlier
        )
        _lambda = scale
        # Note that "Arrival time" has gamma distribution and
        #   "Arrival Interval" has poisson distribution.
        #   We are fitting with gamma dist to reduce computation overhead.
        kstest_res = kstest(self.ts, "gamma", (a, floc, scale))
        pvalue = kstest_res.pvalue
        return a, pvalue

    # lambda_hat = attrs.bproperty(type_cls=float)

    # @lambda_hat.getter
    # def lambda_hat(self):
    #     return self.mean


    n = attrs.integer()
    @n.getter
    def n(self):
        return len(self.ride_times)

    # standard_error = attrs.bproperty(type_cls=float)
    # @standard_error.getter
    # def standard_error(self):
    #     from math import sqrt
    #     return sqrt(self.lambda_hat/self.n)

    chi_sq = attrs.bproperty(type_cls=float)
    @chi_sq.getter
    def chi_sq(self):

        def d(val):
            return (val-self.mean) ** 2

        return avg(d(val) for val in self.ride_times )

