import threading
from math import inf
from collections import defaultdict
import bisect


class SnapshotContainer:
    """
    Stores all business properties of an instance of view model

    For now similar to a dictionary, but might change to pickledb
        for debugging and testing the code.

    """

    def __init__(self):
        self.d = defaultdict(list)
        self.store = dict()
        self.lock = threading.Lock()
        self._read_times = [(-inf, -inf)]

    # def get(self, key):
    #     return self.store[key]
    #
    # def set(self, key, val):
    #     self.store[key] = val

    def set_with_timestamp(self, key: str, val, timestamp: tuple=None) -> None:
        self.store[(timestamp, key)] = val
        self.d[key].append(timestamp)
        # Since the timestamps for all TimeMap.set operations
        #   are strictly increasing
        # self.d[key].sort()

    def set(self, key: str, val, timestamp: tuple=None) -> None:
        self.store[(timestamp, key)] = val
        self.d[key].append(timestamp)
        # Since the timestamps for all TimeMap.set operations
        #   are strictly increasing
        # self.d[key].sort()

    def has_previous(self, key: str):
        return len(self.d[key]) != 0

    def previous(self, key):
        ts = self.d[key][-1]
        return self.store[(ts, key)]

    def get(self, key: str, timestamp: tuple=None):
        if timestamp is None:
            return self.store[(timestamp, key)]

        idx = bisect.bisect_right(self.d[key], timestamp)
        if idx == 0:
            raise AttributeError
        else:
            ts = self.d[key][idx - 1]
            return self.store[(ts, key)]

    from math import inf

    def get_with_range(self, key, lo_excl=(-inf,-inf), hi_incl=(inf,inf)):
        """ NOTE: low is exclusive and high is inclusive (different from range)

        :param key:
        :param lo_excl:
        :param hi_incl:
        :return:
        """
        start_idx = bisect.bisect_right(self.d[key], lo_excl)
        end_idx = bisect.bisect_right(self.d[key], hi_incl)
        for ts in self.d[key][start_idx:end_idx]:
            yield self.store[(ts, key)]
