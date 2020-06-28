import collections
import abc


class Reference(collections.UserString):
    """
    example: '/myusername/'
    """

    def __init__(self, *, _s=None):
        if _s is None:
            _s = ''
        super().__init__(_s)

    def child(self, s):
        return self.__class__(_s=f'{self}/{s}')

    @property
    def first(self):
        return self.data.split('/')[1]  # example: '/myusername/'

    @property
    def last(self):
        return self.data.split('/')[-1]

    @property
    def params(self):
        seq = self.data.split('/')


class Snapshot(collections.UserDict):

    def to_dict(self):
        return self.data.copy()


class Database:

    @classmethod
    @abc.abstractmethod
    def save(cls, ref: Reference, snapshot: Snapshot):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def get(cls, ref: Reference):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def update(cls, ref: Reference, snapshot: Snapshot):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def create(cls, ref: Reference, snapshot: Snapshot):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def delete(cls, ref: Reference):
        raise NotImplementedError

    listener = None


class Listener:

    def on_write(self):
        pass
