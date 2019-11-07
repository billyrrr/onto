

class SnapshotContainer:
    """
    Stores all business properties of an instance of view model

    For now similar to a dictionary, but might change to pickledb
        for debugging and testing the code.

    """

    def __init__(self):
        self.store = dict()

    def get(self, key):
        return self.store[key]

    def set(self, key, val):
        self.store[key] = val

