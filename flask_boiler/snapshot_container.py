import threading
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

    # def get(self, key):
    #     return self.store[key]
    #
    # def set(self, key, val):
    #     self.store[key] = val

    def set(self, key: str, val, timestamp: int=None) -> None:
        self.store[(timestamp, key)] = val
        self.d[key].append(timestamp)
        # Since the timestamps for all TimeMap.set operations
        #   are strictly increasing
        # self.d[key].sort()

    def get(self, key: str, timestamp: int=None):
        idx = bisect.bisect_right(self.d[key], timestamp)
        if idx == 0:
            raise AttributeError
        else:
            ts = self.d[key][idx - 1]
            return self.store[(ts, key)]
